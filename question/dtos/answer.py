from datetime import datetime
from typing import List, Optional, ClassVar

from pydantic import BaseModel, Field, root_validator

from question.models import Question, UserQuestionAnswer
from question.consts import QuestionType, AnswerStatus


class AnswerRequestDto(BaseModel):
    answer: Optional[str] = Field(None, description="답변 내용")
    files: List[str] = Field(default=[], description="첨부 파일 목록 (S3 file paths)")
    
    # validator에서 사용하기 위한 question 객체 저장
    _question: ClassVar[Question] = None
    
    @classmethod
    def set_question(cls, question: Question):
        cls._question = question
    
    @root_validator
    def validate_by_question_types(cls, values):
        if not cls._question:
            raise ValueError("Question이 설정되지 않았습니다")
            
        question_types = cls._question.question_types
        
        # text type 검증
        if QuestionType.TEXT.value in question_types and not values.get('answer'):
            raise ValueError({
                'answer': ['텍스트 답변은 필수입니다']
            })
            
        # file type 검증
        if QuestionType.FILE.value in question_types and not values.get('files'):
            raise ValueError({
                'files': ['파일 첨부는 필수입니다']
            })
            
        return values


class AnswerDataDto(BaseModel):
    id: int
    answer: str
    submitted_at: datetime
    validation_type: str
    status: str
    feedback: Optional[str] = None

    @classmethod
    def by_user_answer(cls, user_answer: UserQuestionAnswer) -> 'AnswerDataDto':
        status = (
            AnswerStatus.SUCCESS.value if user_answer.is_correct is True
            else AnswerStatus.FAILED.value if user_answer.is_correct is False
            else AnswerStatus.PENDING.value
        )

        return cls(
            id=user_answer.id,
            answer=user_answer.answer,
            submitted_at=user_answer.created_at,
            validation_type=user_answer.question.answer_validation_type,
            status=status,
            feedback=user_answer.feedback
        )


class AnswerResponseDto(BaseModel):
    status_code: str = "20100000"
    data: AnswerDataDto 