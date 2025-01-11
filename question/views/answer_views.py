from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsMemberLogin
from question.exceptions import QuestionNotFoundException
from question.consts import QuestionInvalidInputResponseErrorStatus
from question.dtos.answer import (
    AnswerRequestDto,
    MemberAnswerDataDto,
)
from question.services.member_answer_service import MemberAnswerService
from question.models import Question


class AnswerSubmitView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

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

        member_answer_service = MemberAnswerService(
            question=question,
            member_id=request.member.id
        )

        # 답변 제출 권한 체크
        member_answer_service._check_permission()

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

        member_answer = member_answer_service.create_answer(
            answer=request_dto.answer,
            files=request_dto.files
        )

        response_dto = BaseFormatResponse(
            status_code='20100000',
            data=MemberAnswerDataDto.by_member_answer(
                member_answer,
                [
                    int(completed_node_history.node_id)
                    for completed_node_history in member_answer_service.node_completion_result.new_completed_node_histories
                ],
            ).model_dump()
        )

        return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
