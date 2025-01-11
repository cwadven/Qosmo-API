import re
from abc import ABC, abstractmethod
from typing import List, Optional

from question.models import Question, QuestionAnswer
from question.models import QuestionType


class AnswerValidationStrategy(ABC):
    @abstractmethod
    def validate(self, user_answer: str, correct_answers: List[QuestionAnswer]) -> Optional[bool]:
        pass


class TextExactValidationStrategy(AnswerValidationStrategy):
    def validate(self, user_answer: str, correct_answers: List[QuestionAnswer]) -> Optional[bool]:
        return any(user_answer == qa.answer for qa in correct_answers)


class TextContainsValidationStrategy(AnswerValidationStrategy):
    def validate(self, user_answer: str, correct_answers: List[QuestionAnswer]) -> Optional[bool]:
        return any(qa.answer in user_answer for qa in correct_answers)


class RegexValidationStrategy(AnswerValidationStrategy):
    def validate(self, user_answer: str, correct_answers: List[QuestionAnswer]) -> Optional[bool]:
        return any(bool(re.match(qa.answer, user_answer)) for qa in correct_answers)


class ManualValidationStrategy(AnswerValidationStrategy):
    def validate(self, user_answer: str, correct_answers: List[QuestionAnswer]) -> Optional[bool]:
        return None


class AnswerValidationService:
    _strategies = {
        'text_exact': TextExactValidationStrategy(),
        'text_contains': TextContainsValidationStrategy(),
        'regex': RegexValidationStrategy(),
        'manual': ManualValidationStrategy(),
    }

    @classmethod
    def validate_answer(cls, question: Question, user_answer: Optional[str]) -> Optional[bool]:
        """
        answer_validation_type에 따라 답변을 검증합니다.
        """
        # by_pass 체크
        if question.is_by_pass:
            return True

        # text type 체크
        if QuestionType.TEXT.value not in question.question_types:
            return None

        if not user_answer:
            return False

        # QuestionAnswer 객체로 정답 목록 조회
        correct_answers = QuestionAnswer.objects.filter(
            question=question,
            is_deleted=False
        )
        
        if not correct_answers.exists():
            return None

        validation_type = question.answer_validation_type
        strategy = cls._strategies.get(validation_type)
        
        if not strategy:
            return None
            
        return strategy.validate(user_answer, correct_answers)
