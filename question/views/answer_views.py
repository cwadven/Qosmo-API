from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from common.common_exceptions import PydanticAPIException
from question.exceptions import QuestionNotFoundException, AnswerPermissionDeniedException
from question.consts import QuestionInvalidInputResponseErrorStatus
from question.dtos.answer import (
    AnswerRequestDto,
    AnswerResponseDto,
    AnswerDataDto,
)
from question.services.member_answer_service import MemberAnswerService
from question.models import Question


class AnswerSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        try:
            question = Question.objects.select_related(
                'map',
            ).get(
                id=question_id,
                is_deleted=False,
            )
        except Question.DoesNotExist:
            raise QuestionNotFoundException()

        try:
            AnswerRequestDto.set_question(question)
            request_dto = AnswerRequestDto(
                answer=request.data.get('answer'),
                files=request.data.get('files', [])
            )
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=QuestionInvalidInputResponseErrorStatus.INVALID_INPUT_ANSWER_PARAM_ERROR_400.label,
                error_code=QuestionInvalidInputResponseErrorStatus.INVALID_INPUT_ANSWER_PARAM_ERROR_400.value,
                errors=e.errors(),
            )

        user_answer = MemberAnswerService.create_answer(
            question=question,
            member_id=request.user.id,
            answer=request_dto.answer,
            files=request_dto.files
        )

        response_dto = AnswerResponseDto(
            data=AnswerDataDto.by_user_answer(user_answer)
        )

        return Response(response_dto.dict(), status=status.HTTP_200_OK)
