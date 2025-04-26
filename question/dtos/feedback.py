from pydantic import BaseModel, Field


class FeedbackRequestDTO(BaseModel):
    is_correct: bool = Field(..., description="정답 여부")
    feedback: str = Field(..., description="피드백 내용")

    @classmethod
    def of(cls, request) -> 'FeedbackRequestDTO':
        return cls(
            is_correct=request.data.get('is_correct'),
            feedback=request.data.get('feedback'),
        )
