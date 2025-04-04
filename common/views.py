import boto3
import requests
from django.conf import settings
from django.urls import reverse

from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus
from common.common_exceptions import PydanticAPIException
from common.common_utils import generate_pre_signed_url_info
from common.consts import (
    FILE_CONSTANCE_TYPES,
    IMAGE_CONSTANCE_TYPES,
)
from common.dtos.request_dtos import GetPreSignedURLRequest
from common.dtos.response_dtos import (
    ConstanceTypeResponse,
    GetPreSignedURLResponse,
    HealthCheckResponse, GetServerPreSignedURLResponse,
)
from common.exceptions import (
    ExternalAPIException,
    InvalidPathParameterException,
)
from common.helpers.constance_helpers import (
    CONSTANCE_TYPE_HELPER_MAPPER,
)
from member.permissions import IsMemberLogin
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework import status
from common.common_decorators.request_decorators import mandatories


BOTO_CLIENT = boto3.client(
    's3',
    region_name='ap-northeast-2',
    aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
)


class HealthCheckView(APIView):
    def get(self, request):
        return Response(HealthCheckResponse(message='OK').model_dump(), status=200)


class ConstanceTypeView(APIView):
    def get(self, request, constance_type: str):
        constance_type_helper = CONSTANCE_TYPE_HELPER_MAPPER.get(constance_type)
        if not constance_type_helper:
            raise InvalidPathParameterException()
        return Response(
            ConstanceTypeResponse(data=constance_type_helper.get_constance_types()).model_dump(),
            status=200,
        )


class GetImagePreSignedURLView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

    def post(self, request, constance_type: str, transaction_pk: str):
        try:
            pre_signed_url_request = GetPreSignedURLRequest.of(request.data)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        if constance_type not in IMAGE_CONSTANCE_TYPES:
            raise InvalidPathParameterException()

        try:
            info = generate_pre_signed_url_info(
                BOTO_CLIENT,
                settings.AWS_S3_BUCKET_NAME,
                pre_signed_url_request.file_name,
                constance_type,
                transaction_pk,
                same_file_name=True,
            )
            url = info['url']
            data = info['fields']
        except Exception:
            raise ExternalAPIException()

        return Response(
            GetPreSignedURLResponse(
                url=url,
                data=data,
            ).model_dump(),
            status=200,
        )


class GetFilePreSignedURLView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

    def post(self, request, constance_type: str, transaction_pk: str):
        try:
            pre_signed_url_request = GetPreSignedURLRequest.of(request.data)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_PRE_SIGNED_URL_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        if constance_type not in FILE_CONSTANCE_TYPES:
            raise InvalidPathParameterException()

        try:
            info = generate_pre_signed_url_info(
                BOTO_CLIENT,
                settings.AWS_S3_BUCKET_NAME,
                pre_signed_url_request.file_name,
                constance_type,
                transaction_pk,
                same_file_name=False,
            )
        except Exception as e:
            print(e)
            raise ExternalAPIException()

        return Response(
            GetServerPreSignedURLResponse(
                data={
                    'url': reverse('common:upload_file'),
                    'extra_data': info['fields'],
                },
            ).model_dump(),
            status=200,
        )


class UploadFilePreSignedURLView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]
    parser_classes = (MultiPartParser, FormParser)

    @mandatories('file', 'key', 'x-amz-algorithm', 'x-amz-credential', 'x-amz-date', 'policy', 'x-amz-signature')
    def post(self, request, m):
        file = request.FILES['file']
        
        try:
            # 클라이언트가 제공한 pre-signed URL 데이터로 구성
            pre_signed_data = {
                'key': m['key'],
                'x-amz-algorithm': m['x-amz-algorithm'],
                'x-amz-credential': m['x-amz-credential'],
                'x-amz-date': m['x-amz-date'],
                'policy': m['policy'],
                'x-amz-signature': m['x-amz-signature']
            }
            
            # requests 라이브러리를 사용하여 S3에 직접 POST 요청
            response = requests.post(
                url=settings.AWS_S3_PRE_SIGNED_UPLOAD_URL,
                data=pre_signed_data,
                files={'file': file.read()},
            )
            
            # HTTP 상태 코드로 성공 여부 확인 (일반적으로 204는 성공)
            if response.status_code == 204:
                # 성공 시 200 OK와 함께 업로드된 파일의 S3 경로 반환
                return Response(
                    {
                        'data': {
                            'message': '파일 업로드 성공',
                            'path': f'{settings.AWS_S3_PRE_SIGNED_UPLOAD_URL}/{m["key"]}'
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # 업로드 실패
                return Response(
                    {'message': f'파일 업로드에 실패했습니다. 상태 코드: {response.status_code}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'message': f'파일 업로드 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
