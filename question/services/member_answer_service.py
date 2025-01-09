from typing import List, Optional

from django.utils import timezone
from django.db import transaction

from question.exceptions import QuestionNotFoundException, AnswerPermissionDeniedException
from question.models import Question, UserQuestionAnswer, UserQuestionAnswerFile
from question.consts import QuestionType
from question.services.answer_validation_service import AnswerValidationService
from question.services.node_completion_service import NodeCompletionService


class MemberAnswerService:
    @staticmethod
    def create_answer(question: Question, member_id: int, answer: Optional[str], files: List[str]) -> UserQuestionAnswer:
        if not MemberAnswerService._check_permission(question, member_id):
            raise AnswerPermissionDeniedException()

        # 정답 검증
        is_correct = AnswerValidationService.validate_answer(question, answer)

        # feedback과 reviewed_at 설정
        feedback = None
        reviewed_at = None
        
        if is_correct is not None:
            reviewed_at = timezone.now()
            if is_correct:
                feedback = question.default_success_feedback
            else:
                feedback = question.default_failure_feedback

        with transaction.atomic():
            user_answer = UserQuestionAnswer.objects.create(
                map=question.map,
                question=question,
                member_id=member_id,
                answer=answer or '',
                is_correct=is_correct,
                feedback=feedback,
                reviewed_by=None,
                reviewed_at=reviewed_at
            )

            if files:
                answer_files = [
                    UserQuestionAnswerFile(
                        map=question.map,
                        question=question,
                        user_question_answer=user_answer,
                        file=file_path
                    )
                    for file_path in files
                ]
                UserQuestionAnswerFile.objects.bulk_create(answer_files)

            # 정답인 경우 노드 완료 프로세스 실행
            if is_correct:
                node_completion_service = NodeCompletionService(member_id=member_id)
                node_completion_service.process_nodes_completion(nodes=[question.node])

            return user_answer

    @staticmethod
    def _check_permission(question: Question, member_id: int) -> bool:
        # 여기에 권한 체크 로직 구현
        return True
