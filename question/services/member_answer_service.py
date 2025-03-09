from typing import List, Optional

from django.db.models import F
from django.utils import timezone
from django.db import transaction

from map.models import ArrowProgress, Node
from member.models import Guest
from play.models import MapPlayMember
from push.consts import PushChannelType
from push.services import PushService
from question.dtos.member_answer_file import MemberAnswerFileDto
from question.dtos.node_completion import NodeCompletionResultDto
from question.exceptions import AnswerPermissionDeniedException
from question.models import Question, UserQuestionAnswer, UserQuestionAnswerFile
from question.services.answer_validation_service import AnswerValidationService
from question.services.node_completion_service import NodeCompletionService
from question.tasks import send_question_submitted_email
from map.models.arrow import Arrow
from map.models.node_history import NodeCompletedHistory


class MemberAnswerService:
    def __init__(
            self,
            question: Question,
            member_id: int,
            map_play_member_id: int,
            map_play_id: int
    ):
        self.question = question
        self.member_id = member_id
        self.map_play_member_id = map_play_member_id
        self.map_play_id = map_play_id
        self._permission_checked = False
        self._not_completed_node_names = None
        self.new_arrow_progresses = []
        self.new_completed_node_histories = []

    def check_permission(self) -> None:
        self._check_permission()

    def _check_permission(self) -> None:
        """
        답변 제출 권한을 체크합니다.
        한 번 체크한 결과는 캐싱됩니다.
        """
        if self._permission_checked:
            if self._not_completed_node_names:
                raise AnswerPermissionDeniedException(
                    error_summary=f"Node '{', '.join(self._not_completed_node_names)}'가 완료되지 않아 답변을 제출할 수 없습니다."
                )
            return

        arrow = Arrow.objects.filter(
            question=self.question,
            is_deleted=False
        ).select_related(
            'start_node',
            'end_node',
        ).first()

        if not arrow:
            self._permission_checked = True
            return

        from_before_arrows = Arrow.objects.filter(
            end_node_id=arrow.start_node_id
        ).exclude(
            end_node_id=F('start_node_id'),
        )

        from_before_arrows_node_completed_ids = NodeCompletedHistory.objects.filter(
            map_id=self.question.map_id,
            node_id__in=from_before_arrows.values_list('start_node_id', flat=True),
            map_play_member__map_play_id=self.map_play_id,
        ).values_list('node_id', flat=True)

        not_completed_node_ids = set(from_before_arrows.values_list('start_node_id', flat=True)) - set(from_before_arrows_node_completed_ids)

        self._permission_checked = True

        if not_completed_node_ids:
            self._not_completed_node_names = list(Node.objects.filter(
                id__in=not_completed_node_ids
            ).values_list(
                'name',
                flat=True,
            ))
            raise AnswerPermissionDeniedException(
                error_summary=f"Node '{', '.join(self._not_completed_node_names)}'가 완료되지 않아 답변을 제출할 수 없습니다."
            )

    def create_answer(self, answer: Optional[str], files: List[MemberAnswerFileDto]) -> UserQuestionAnswer:
        self._check_permission()

        # 정답 검증
        is_correct = AnswerValidationService.validate_answer(self.question, answer)

        # feedback과 reviewed_at 설정
        feedback = None
        reviewed_at = None

        if is_correct is not None:
            reviewed_at = timezone.now()
            if is_correct:
                feedback = self.question.default_success_feedback
            else:
                feedback = self.question.default_failure_feedback

        with transaction.atomic():
            user_answer = UserQuestionAnswer.objects.create(
                map=self.question.map,
                question=self.question,
                member_id=self.member_id,
                map_play_member_id=self.map_play_member_id,
                answer=answer or '',
                is_correct=is_correct,
                feedback=feedback,
                reviewed_by=None,
                reviewed_at=reviewed_at
            )

            if files:
                # 추후에 s3에 올리는 로직 필요
                answer_files = [
                    UserQuestionAnswerFile(
                        map=self.question.map,
                        question=self.question,
                        user_question_answer=user_answer,
                        name=file.name,
                        file=file.url,
                    )
                    for file in files
                ]
                UserQuestionAnswerFile.objects.bulk_create(answer_files)

            # 관리자 수동 검증이 필요한 경우 email 전송
            if is_correct is None:
                send_question_submitted_email.apply_async(
                    (
                        [self.question.map.created_by.email],
                        user_answer.member.nickname,
                        self.question.map.name,
                        self.question.title,
                        answer,
                        [
                            {'name': file.name, 'url': file.url}
                            for file in files
                        ],
                        user_answer.id,
                     )
                )

            # 정답인 경우 Arrow 진행 상태 처리
            if is_correct:
                # Question과 연결된 Arrow 찾기
                arrow = Arrow.objects.filter(
                    map=self.question.map,
                    question=self.question,
                    is_deleted=False
                ).select_related(
                    'start_node',
                    'node_complete_rule',
                ).first()

                if arrow:
                    now = timezone.now()
                    # 현재 Arrow의 ArrowProgress 생성
                    _, created = ArrowProgress.objects.get_or_create(
                        map=self.question.map,
                        arrow=arrow,
                        member_id=self.member_id,
                        map_play_member_id=self.map_play_member_id,
                        is_resolved=True,
                        resolved_at=now
                    )
                    if not created:
                        return user_answer

                    # 같은 규칙에 묶인 Arrow들의 진행 상태 확인
                    rule_arrow_ids = Arrow.objects.filter(
                        node_complete_rule=arrow.node_complete_rule,
                        is_deleted=False
                    ).values_list(
                        'id',
                        flat=True,
                    )
                    completed_arrow_ids = set(
                        ArrowProgress.objects.filter(
                            arrow__in=rule_arrow_ids,
                            map_play_member__map_play_id=self.map_play_id,
                            is_resolved=True
                        ).values_list(
                            'arrow_id',
                            flat=True,
                        )
                    )

                    # 모든 Arrow가 completed 상태인 경우 NodeCompletionService 호출
                    if len(rule_arrow_ids) <= len(completed_arrow_ids):
                        node_completion_service = NodeCompletionService(
                            member_id=self.member_id,
                            map_play_member_id=self.map_play_member_id,
                            map_play_id=self.map_play_id,
                        )
                        completion_result = node_completion_service.process_nodes_completion(nodes=[arrow.start_node])

                        # 결과 누적
                        self.new_arrow_progresses.extend(completion_result.new_arrow_progresses)
                        self.new_completed_node_histories.extend(completion_result.new_completed_node_histories)

                push_service = PushService()
                map_play_members = MapPlayMember.objects.filter(
                    map_play_id=self.map_play_id,
                    deactivated=False,
                ).exclude(
                    member_id=self.member_id,
                )
                if map_play_members:
                    guests = Guest.objects.filter(
                        member_id__in=[map_play_member.member_id for map_play_member in map_play_members],
                        member__is_active=True,
                    )
                    for guest in guests:
                        push_service.send_push(
                            guest_id=guest.id,
                            title=f"\'{user_answer.question.title}\' 문제 해결",
                            body=f"{user_answer.member.nickname}님이 문제를 해결했습니다.",
                            push_channel_type=PushChannelType.QUESTION_SOLVED_ALERT,
                            data={
                                "type": "question_solved_alert",
                                "question_id": str(user_answer.question.id),
                                "map_id": str(arrow.map_id),
                                "map_play_id": str(user_answer.map_play_member.map_play_id),
                                "is_correct": True,
                            },
                        )

            return user_answer

    @property
    def node_completion_result(self) -> NodeCompletionResultDto:
        """
        누적된 노드 완료 결과를 반환합니다.
        """
        return NodeCompletionResultDto(
            new_arrow_progresses=self.new_arrow_progresses,
            new_completed_node_histories=self.new_completed_node_histories
        )
