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
from question.exceptions import AnswerPermissionDeniedException, AnswerNotFoundException
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
                    error_summary=f"'{', '.join(self._not_completed_node_names)}'가 완료되지 않아 답변을 제출할 수 없습니다."
                )
            return

        if not self.question.arrow:
            self._permission_checked = True
            return

        # 문제를 제외한 (exclude : node_complete_rule__node_id==start_node_id)
        # 현재 NodeCompleteRule 을 바라보고 있는 모든 화살표들
        from_before_node_complete_rule_arrows = Arrow.objects.select_related(
            'start_node',
        ).filter(
            node_complete_rule_id=self.question.arrow.node_complete_rule_id,
        ).exclude(
            node_complete_rule__node_id=F('start_node_id'),
        )
        # 바라보는 화살표들의 해당 Node 들
        before_nodes = [
            from_before_node_complete_rule_arrow.start_node
            for from_before_node_complete_rule_arrow in from_before_node_complete_rule_arrows
        ]
        before_node_ids = [before_node.id for before_node in before_nodes]
        # 그 Node 중에서 해결된 것들을 확인하는 쿼리
        from_before_arrows_node_completed_ids = NodeCompletedHistory.objects.filter(
            map_id=self.question.map_id,
            node_id__in=before_node_ids,
            map_play_member__map_play_id=self.map_play_id,
        ).values_list('node_id', flat=True)

        # 모든 것과 완결된 거를 차집합 하는 경우, 만약 풀리지 않은 게 있으면 그 id
        not_completed_node_ids = set(before_node_ids) - set(from_before_arrows_node_completed_ids)

        self._permission_checked = True

        if not_completed_node_ids:
            # 해결되지 않은 Node 이름을 가져옵니다.
            self._not_completed_node_names = list(
                map(
                    lambda x: x.name,
                    filter(
                        lambda x: x.id in not_completed_node_ids,
                        before_nodes,
                    )
                )
            )
            raise AnswerPermissionDeniedException(
                error_summary=f"'{', '.join(self._not_completed_node_names)}'가 완료되지 않아 답변을 제출할 수 없습니다."
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
                now = timezone.now()
                # 현재 Arrow의 ArrowProgress 생성
                _, created = ArrowProgress.objects.get_or_create(
                    map=self.question.map,
                    arrow=self.question.arrow,
                    member_id=self.member_id,
                    map_play_member_id=self.map_play_member_id,
                    is_resolved=True,
                    resolved_at=now
                )
                if not created:
                    return user_answer

                # 같은 규칙에 묶인 Arrow들의 진행 상태 확인
                rule_connected_arrow_ids = Arrow.objects.filter(
                    node_complete_rule=self.question.arrow.node_complete_rule,
                    is_deleted=False
                ).values_list(
                    'id',
                    flat=True,
                )
                completed_arrow_ids = set(
                    ArrowProgress.objects.filter(
                        arrow__in=rule_connected_arrow_ids,
                        map_play_member__map_play_id=self.map_play_id,
                        is_resolved=True
                    ).values_list(
                        'arrow_id',
                        flat=True,
                    )
                )

                # 모든 Arrow가 completed 상태인 경우 NodeCompletionService 호출
                if len(rule_connected_arrow_ids) <= len(completed_arrow_ids):
                    node_completion_service = NodeCompletionService(
                        member_id=self.member_id,
                        map_play_member_id=self.map_play_member_id,
                        map_play_id=self.map_play_id,
                    )
                    completion_result = node_completion_service.process_nodes_completion(
                        nodes=[self.question.arrow.start_node]
                    )

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
                                "map_id": str(self.question.arrow.map_id),
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

    @staticmethod
    def get_answer_detail(user_question_answer_id: int, member_id: int) -> 'UserQuestionAnswer':
        """
        사용자의 문제 답변 상세 정보를 조회합니다.
        
        Args:
            user_question_answer_id: 조회할 답변 ID
            member_id: 조회하는 사용자 ID
            
        Returns:
            UserQuestionAnswer: 답변 상세 정보
            
        Raises:
            AnswerPermissionDeniedException: 조회 권한이 없는 경우
            AnswerNotFoundException: 답변을 찾을 수 없는 경우
        """
        try:
            answer = UserQuestionAnswer.objects.select_related(
                'question',
                'map_play_member',
                'map_play_member__member',
                'reviewed_by',
            ).prefetch_related(
                'files',
            ).get(
                id=user_question_answer_id,
            )
            
            # 답변 작성자 본인 또는 Map 생성자만 조회 가능
            if member_id != answer.map_play_member.member_id and member_id != answer.map.created_by_id:
                raise AnswerPermissionDeniedException()
                
            return answer
            
        except UserQuestionAnswer.DoesNotExist:
            raise AnswerNotFoundException()

    @staticmethod
    def submit_feedback(
        user_question_answer_id: int,
        member_id: int,
        is_correct: bool,
        feedback: str,
    ) -> 'UserQuestionAnswer':
        """
        사용자의 문제 답변에 대한 피드백을 제출합니다.
        
        Args:
            user_question_answer_id: 답변 ID
            member_id: 피드백 제출자 ID
            is_correct: 정답 여부
            feedback: 피드백 내용
            
        Returns:
            UserQuestionAnswer: 업데이트된 답변 정보
            
        Raises:
            AnswerPermissionDeniedException: 피드백 제출 권한이 없는 경우
            AnswerNotFoundException: 답변을 찾을 수 없는 경우
        """
        try:
            answer = UserQuestionAnswer.objects.select_related(
                'map',
                'map_play_member',
                'map_play_member__member',
                'reviewed_by',
            ).get(
                id=user_question_answer_id,
            )
            
            # Map 생성자만 피드백 제출 가능
            if member_id != answer.map.created_by_id:
                raise AnswerPermissionDeniedException()
            
            # 피드백 업데이트
            answer.is_correct = is_correct
            answer.feedback = feedback
            answer.reviewed_by_id = member_id
            answer.reviewed_at = timezone.now()
            answer.save(update_fields=['is_correct', 'feedback', 'reviewed_by', 'reviewed_at'])

            push_service = PushService()

            try:
                answer_owner = Guest.objects.get(
                    member_id=answer.member_id,
                    member__is_active=True,
                )
                push_service.send_push(
                    guest_id=answer_owner.id,
                    title=f"\'{answer.question.title}\' 문제 결과",
                    body=feedback,
                    push_channel_type=PushChannelType.QUESTION_FEEDBACK,
                    data={
                        "type": "question_feedback",
                        "question_id": str(answer.question.id),
                        "map_id": str(answer.map_id),
                        "map_play_member_id": str(answer.map_play_member_id),
                        "is_correct": str(answer.is_correct).lower(),
                    },
                )
            except Guest.DoesNotExist:
                pass
            
            # 정답인 경우 노드 완료 처리
            if is_correct:
                node_completion_service = NodeCompletionService(
                    member_id=answer.map_play_member.member_id,
                    map_play_member_id=answer.map_play_member_id,
                    map_play_id=answer.map_play_member.map_play_id,
                )
                node_completion_service.process_nodes_completion(nodes=[answer.question.arrow.start_node])
                
                # 푸시 알림 전송
                map_play_members = MapPlayMember.objects.filter(
                    map_play_id=answer.map_play_member.map_play_id,
                    deactivated=False,
                ).exclude(
                    member_id=answer.map_play_member.member_id,
                )
                if map_play_members:
                    guests = Guest.objects.filter(
                        member_id__in=[map_play_member.member_id for map_play_member in map_play_members],
                        member__is_active=True,
                    )
                    for guest in guests:
                        push_service.send_push(
                            guest_id=guest.id,
                            title=f"\'{answer.question.title}\' 문제 해결",
                            body=f"{answer.member.nickname}님이 문제를 해결했습니다.",
                            push_channel_type=PushChannelType.QUESTION_SOLVED_ALERT,
                            data={
                                "type": "question_solved_alert",
                                "question_id": str(answer.question.id),
                                "map_id": str(answer.map_id),
                                "map_play_id": str(answer.map_play_member.map_play_id),
                                "is_correct": True,
                            },
                        )
            
            return answer
            
        except UserQuestionAnswer.DoesNotExist:
            raise AnswerNotFoundException()
