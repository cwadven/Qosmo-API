import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from common.common_exceptions import PydanticAPIException
from common.common_utils import generate_pre_signed_url_info, upload_file_to_pre_signed_url
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsMemberLogin
from node.services.node_detail_service import find_activatable_node_ids_after_completion
from play.services import MapPlayService
from question.dtos.member_answer_file import MemberAnswerFileDto
from question.exceptions import QuestionNotFoundException
from question.consts import QuestionInvalidInputResponseErrorStatus
from question.dtos.answer import (
    AnswerRequestDto,
    MemberAnswerDataDto,
)
from question.services.member_answer_service import MemberAnswerService
from question.models import Question


BOTO_CLIENT = boto3.client(
    's3',
    region_name='ap-northeast-2',
    aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
)


class AnswerSubmitView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]
    map_play_service = MapPlayService()

    def post(self, request, question_id: int, map_play_member_id: int):
        try:
            question = Question.objects.select_related(
                'map',
            ).get(
                id=question_id,
                is_deleted=False,
            )
        except Question.DoesNotExist:
            raise QuestionNotFoundException()

        map_play_member = self.map_play_service._get_map_play_member_by_id(map_play_member_id)
        self.map_play_service.validate_map_and_play_member_access(
            question.map_id,
            request.guest.member_id,
            map_play_member.id,
        )

        member_answer_service = MemberAnswerService(
            question=question,
            member_id=request.guest.member_id,
            map_play_member_id=map_play_member_id,
            map_play_id=map_play_member.map_play_id,
        )

        # 답변 제출 권한 체크
        member_answer_service.check_permission()

        try:
            AnswerRequestDto.set_question(question)
            request_dto = AnswerRequestDto(
                answer=request.data.get('answer'),
                files=request.FILES.getlist('files'),
            )
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=QuestionInvalidInputResponseErrorStatus.INVALID_INPUT_ANSWER_PARAM_ERROR_400.label,
                error_code=QuestionInvalidInputResponseErrorStatus.INVALID_INPUT_ANSWER_PARAM_ERROR_400.value,
                errors=e.errors(),
            )

        files = []
        client = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        for file in request_dto.files:
            response = generate_pre_signed_url_info(
                client,
                settings.AWS_S3_BUCKET_NAME,
                file.name,
                'member-answer-file',
                str(question_id),
            )
            upload_file_to_pre_signed_url(
                response['url'],
                response['fields'],
                file.read(),
            )
            files.append(
                MemberAnswerFileDto(
                    id=None,
                    name=file.name,
                    url=response['url'] + response['fields']['key'],
                )
            )

        # 추후에 s3 올리는 file 로직 필요
        member_answer = member_answer_service.create_answer(
            answer=request_dto.answer,
            files=files,
        )
        completed_node_ids = [
            node_history.node_id
            for node_history in member_answer_service.new_completed_node_histories
        ]
        completed_arrow_ids = [
            arrow_progress.arrow_id
            for arrow_progress in member_answer_service.new_arrow_progresses
        ]
        going_to_in_progress_node_ids = find_activatable_node_ids_after_completion(
            request.guest.member_id,
            completed_node_ids,
        )

        response_dto = BaseFormatResponse(
            status_code='success',
            data=MemberAnswerDataDto.of(
                member_answer,
                list(going_to_in_progress_node_ids),
                completed_node_ids,
                completed_arrow_ids,
            ).model_dump()
        )

        return Response(response_dto.model_dump(), status=status.HTTP_201_CREATED)
