from typing import List, Optional

from django.db.models import F
from django.utils import timezone
from django.db import transaction

from map.models import ArrowProgress, Node
from question.exceptions import AnswerPermissionDeniedException
from question.models import Question, UserQuestionAnswer, UserQuestionAnswerFile
from question.services.answer_validation_service import AnswerValidationService
from question.services.node_completion_service import NodeCompletionService
from map.models.arrow import Arrow
from map.models.node_history import NodeCompletedHistory


class MemberAnswerService:
    def __init__(self, question: Question, member_id: int):
        self.question = question
        self.member_id = member_id
        self._permission_checked = False
        self._not_completed_node_names = None

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
            member_id=self.member_id
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

    def create_answer(self, answer: Optional[str], files: List[str]) -> UserQuestionAnswer:
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
                answer=answer or '',
                is_correct=is_correct,
                feedback=feedback,
                reviewed_by=None,
                reviewed_at=reviewed_at
            )

            if files:
                answer_files = [
                    UserQuestionAnswerFile(
                        map=self.question.map,
                        question=self.question,
                        user_question_answer=user_answer,
                        file=file_path
                    )
                    for file_path in files
                ]
                UserQuestionAnswerFile.objects.bulk_create(answer_files)

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
                    completed_arrow_ids = ArrowProgress.objects.filter(
                        arrow__in=rule_arrow_ids,
                        member_id=self.member_id,
                        is_resolved=True
                    ).values_list(
                        'arrow_id',
                        flat=True,
                    )

                    # 모든 Arrow가 completed 상태인 경우 NodeCompletionService 호출
                    if len(rule_arrow_ids) <= len(completed_arrow_ids):
                        node_completion_service = NodeCompletionService(member_id=self.member_id)
                        node_completion_service.process_nodes_completion(nodes=[arrow.start_node])

            return user_answer
