from datetime import datetime
from typing import List, Optional, ClassVar

from pydantic import BaseModel, Field, field_validator

from question.models import Question, UserQuestionAnswer
from question.consts import QuestionType, AnswerStatus


class AnswerRequestDto(BaseModel):
    answer: Optional[str] = Field(None, description="답변 내용")
    files: List[str] = Field(default=[], description="첨부 파일 목록 (S3 file paths)")
    
    _question: ClassVar[Question] = None
    
    @classmethod
    def set_question(cls, question: Question):
        cls._question = question
    
    @field_validator(
        'answer',
        mode='before'
    )
    def validate_answer(cls, value: Optional[str]) -> Optional[str]:
        if not cls._question:
            raise ValueError('Question이 설정되지 않았습니다')
            
        if QuestionType.TEXT.value in cls._question.question_types and not value:
            raise ValueError('텍스트 답변은 필수입니다')
            
        return value

    @field_validator(
        'files',
        mode='before'
    )
    def validate_files(cls, value: List[str]) -> List[str]:
        if not cls._question:
            raise ValueError('Question이 설정되지 않았습니다')
            
        if QuestionType.FILE.value in cls._question.question_types and not value:
            raise ValueError('파일 첨부는 필수입니다')
            
        return value


class MemberAnswerDataDto(BaseModel):
    member_answer_id: int
    answer: str
    submitted_at: datetime
    validation_type: str
    status: str
    feedback: Optional[str] = None

    @classmethod
    def by_user_answer(cls, member_answer: UserQuestionAnswer) -> 'AnswerDataDto':
        status = (
            AnswerStatus.SUCCESS.value if member_answer.is_correct is True
            else AnswerStatus.FAILED.value if member_answer.is_correct is False
            else AnswerStatus.PENDING.value
        )

        return cls(
            member_answer_id=member_answer.id,
            answer=member_answer.answer,
            submitted_at=member_answer.created_at,
            validation_type=member_answer.question.answer_validation_type,
            status=status,
            feedback=member_answer.feedback
        )


class AnswerResponseDto(BaseModel):
    status_code: str = "20100000"
    data: MemberAnswerDataDto
