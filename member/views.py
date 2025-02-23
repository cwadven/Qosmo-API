import boto3
import jwt
from botocore.config import Config
from django.conf import settings

from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus
from common.common_consts.common_status_codes import SuccessStatusCode
from common.common_decorators.request_decorators import mandatories
from common.common_exceptions import PydanticAPIException
from common.common_utils import (
    generate_pre_signed_url_info,
    generate_random_string_digits,
    get_jwt_guest_token,
    get_jwt_login_token,
    get_jwt_refresh_token,
    get_request_ip,
    upload_file_to_pre_signed_url,
)
from common.common_utils.cache_utils import (
    delete_cache_value_by_key,
    generate_dict_value_by_key_to_cache,
    get_cache_value_by_key,
    increase_cache_int_value_by_key,
)
from common.dtos.response_dtos import BaseFormatResponse
from config.middlewares.authentications import jwt_decode_handler, jwt_decode_refresh_token_handler
from django.contrib.auth import (
    authenticate,
)
from django.db import transaction
from member.consts import (
    MemberCreationExceptionMessage,
    MemberProviderEnum,
    MemberStatusEnum,
    MemberTypeEnum,
    SIGNUP_EMAIL_TOKEN_TTL,
    SIGNUP_MACRO_COUNT,
    SIGNUP_MACRO_VALIDATION_KEY,
)
from member.dtos.request_dtos import (
    ChangeProfileRequest,
    NormalLoginRequest,
    RefreshTokenRequest,
    SignUpEmailTokenSendRequest,
    SignUpEmailTokenValidationEndRequest,
    SignUpValidationRequest,
    SocialLoginRequest,
    SocialSignUpRequest,
)
from member.dtos.response_dtos import (
    GuestTokenGetOrCreateResponse,
    NormalLoginResponse,
    RefreshTokenResponse,
    SocialLoginResponse, ProfileData,
)
from member.exceptions import (
    AlreadyMemberExistsErrorException,
    InvalidRefreshTokenErrorException,
    InvalidValueForSignUpFieldErrorException,
    LoginFailedException,
    MemberCreationErrorException,
    NoMemberRefreshTokenErrorException,
    NormalLoginFailedException,
    SignUpEmailTokenErrorException,
    SignUpEmailTokenExpiredErrorException,
    SignUpEmailTokenInvalidErrorException,
    SignUpEmailTokenMacroErrorException,
)
from member.models import (
    Guest,
    Member,
)
from member.services import (
    check_email_exists,
    check_nickname_exists,
    check_username_exists,
    get_member_profile,
)
from member.tasks import send_one_time_token_email
from member.validators.sign_up_validators import SignUpPayloadValidator
from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from member.permissions import IsMemberLogin


class LoginView(APIView):
    @mandatories('username', 'password')
    def post(self, request, m):
        normal_login_request = NormalLoginRequest(
            username=m['username'],
            password=m['password'],
        )
        member = authenticate(
            request,
            username=normal_login_request.username,
            password=normal_login_request.password
        )
        if not member:
            raise NormalLoginFailedException()

        normal_login_response = NormalLoginResponse(
            access_token=get_jwt_login_token(member),
            refresh_token=get_jwt_refresh_token(member.guest),
        )
        return Response(normal_login_response.model_dump(), status=200)


class SocialLoginView(APIView):
    @mandatories('provider', 'token')
    @transaction.atomic
    def post(self, request, m):
        social_login_request = SocialLoginRequest(
            token=m['token'],
            provider=m['provider'],
        )
        member = Member.objects.get_member_by_token(
            social_login_request.token,
            social_login_request.provider,
        )
        if not member:
            raise LoginFailedException()
        member.raise_if_inaccessible()

        social_login_response = SocialLoginResponse(
            access_token=get_jwt_login_token(member),
            refresh_token=get_jwt_refresh_token(member.guest),
        )
        return Response(social_login_response.model_dump(), status=200)


class SocialSignUpView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            social_sign_up_request = SocialSignUpRequest.of(request.data)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_SIGN_UP_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_SIGN_UP_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        member, is_created = Member.objects.get_or_create_member_by_token(
            social_sign_up_request.token,
            social_sign_up_request.provider,
        )
        if is_created:
            if not request.guest:
                request.guest = Guest(ip=get_request_ip(request))
            request.guest.temp_nickname = member.nickname
            request.guest.email = member.email
            request.guest.member = member
            request.guest.save()
        else:
            raise AlreadyMemberExistsErrorException()

        social_login_response = SocialLoginResponse(
            access_token=get_jwt_login_token(member),
            refresh_token=get_jwt_refresh_token(member.guest),
        )
        return Response(social_login_response.model_dump(), status=200)


class RefreshTokenView(APIView):
    @mandatories('refresh_token')
    def post(self, request, m):
        refresh_token_request = RefreshTokenRequest(
            refresh_token=m['refresh_token'],
        )
        try:
            payload = jwt_decode_refresh_token_handler(refresh_token_request.refresh_token)
            member = Member.objects.get(id=payload.get('member_id'))
            refresh_token_response = RefreshTokenResponse(
                access_token=get_jwt_login_token(member),
                refresh_token=get_jwt_refresh_token(member.guest),
            )
        except jwt.InvalidTokenError:
            raise InvalidRefreshTokenErrorException()
        except Member.DoesNotExist:
            raise NoMemberRefreshTokenErrorException()
        return Response(refresh_token_response.model_dump(), status=200)


class SignUpEmailTokenSendView(APIView):
    @mandatories('email', 'nickname', 'password2')
    def post(self, request, m):
        sign_up_email_token_send_request = SignUpEmailTokenSendRequest(
            email=m['email'],
            nickname=m['nickname'],
            password2=m['password2'],
        )
        generate_dict_value_by_key_to_cache(
            key=sign_up_email_token_send_request.email,
            value={
                'one_time_token': generate_random_string_digits(),
                'email': sign_up_email_token_send_request.email,
                'nickname': sign_up_email_token_send_request.nickname,
                'password2': sign_up_email_token_send_request.password2,
            },
            expire_seconds=SIGNUP_EMAIL_TOKEN_TTL
        )
        value = get_cache_value_by_key(sign_up_email_token_send_request.email)
        if value:
            send_one_time_token_email.apply_async(
                (
                    sign_up_email_token_send_request.email,
                    value['one_time_token'],
                )
            )
            return Response({'message': '인증번호를 이메일로 전송했습니다.'}, 200)
        raise SignUpEmailTokenErrorException()


class SignUpEmailTokenValidationEndView(APIView):
    @mandatories('email', 'one_time_token')
    @transaction.atomic
    def post(self, request, m):
        payload = SignUpEmailTokenValidationEndRequest(
            email=m['email'],
            one_time_token=m['one_time_token']
        )
        macro_count = increase_cache_int_value_by_key(
            key=SIGNUP_MACRO_VALIDATION_KEY.format(payload.email),
        )
        if macro_count >= SIGNUP_MACRO_COUNT:
            raise SignUpEmailTokenMacroErrorException(
                error_summary=SignUpEmailTokenMacroErrorException.default_detail.format(
                    SIGNUP_MACRO_COUNT,
                    24
                )
            )

        value = get_cache_value_by_key(payload.email)

        if not value:
            raise SignUpEmailTokenExpiredErrorException()

        if not value.get('one_time_token') or value.get('one_time_token') != payload.one_time_token:
            raise SignUpEmailTokenInvalidErrorException(
                errors={'one_time_token': ['인증번호가 다릅니다.']}
            )
        if check_nickname_exists(value['nickname']):
            raise MemberCreationErrorException(
                error_summary=MemberCreationExceptionMessage.NICKNAME_EXISTS.label
            )
        if check_email_exists(value['email']):
            raise MemberCreationErrorException(
                error_summary=MemberCreationExceptionMessage.EMAIL_EXISTS.label
            )

        member = Member.objects.create_user(
            username=value['email'],
            nickname=value['nickname'],
            email=value['email'],
            member_type_id=MemberTypeEnum.NORMAL_MEMBER.value,
            member_status_id=MemberStatusEnum.NORMAL_MEMBER.value,
            password=value['password2'],
            member_provider_id=MemberProviderEnum.EMAIL.value,
        )
        if not request.guest:
            request.guest = Guest(ip=get_request_ip(request))
        request.guest.temp_nickname = member.nickname
        request.guest.email = member.email
        request.guest.member = member
        request.guest.save()

        delete_cache_value_by_key(value['email'])
        delete_cache_value_by_key(SIGNUP_MACRO_VALIDATION_KEY.format(payload.email))
        return Response({'message': '회원가입에 성공했습니다.'}, 200)


class SignUpValidationView(APIView):
    @mandatories('email', 'nickname', 'password1', 'password2')
    def post(self, request, m):
        payload = SignUpValidationRequest(
            email=m['email'],
            nickname=m['nickname'],
            password1=m['password1'],
            password2=m['password2'],
        )
        payload_validator = SignUpPayloadValidator(payload.model_dump())
        error_dict = payload_validator.validate()
        if error_dict:
            raise InvalidValueForSignUpFieldErrorException(errors=error_dict)
        return Response({'message': 'success'}, 200)


class GetOrCreateGuestTokenView(APIView):
    def post(self, request):
        ip = get_request_ip(request)
        guest = Guest.objects.filter(
            ip=ip,
            member__isnull=True,
        ).last()
        if not guest:
            guest = Guest.objects.create(
                ip=ip,
                temp_nickname=f'비회원{generate_random_string_digits(8)}'
            )
        guest_token_get_or_create_response = GuestTokenGetOrCreateResponse(
            access_token=get_jwt_guest_token(guest),
            refresh_token=get_jwt_refresh_token(guest),
        )
        return Response(guest_token_get_or_create_response.model_dump(), status=200)


class ProfileView(APIView):
    permission_classes = [IsMemberLogin]

    def get(self, request):
        profile_data = get_member_profile(request.guest.member_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=ProfileData(
                    id=profile_data['id'],
                    nickname=profile_data['nickname'],
                    profile_image=profile_data['profile_image'],
                    subscribed_map_count=profile_data['subscribed_map_count'],
                ).model_dump(),
            ).model_dump(),
            status=200,
        )

    def patch(self, request):
        try:
            request_change_profile = ChangeProfileRequest(
                nickname=request.data.get('nickname'),
                profile_image=request.FILES.get('profile_image'),
            )
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_PROFILE_CHANGE_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_PROFILE_CHANGE_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        try:
            member = Member.objects.get(id=request.guest.member_id)
        except Member.DoesNotExist:
            raise LoginFailedException()
        member.raise_if_inaccessible()

        update_fields = []
        if request_change_profile.nickname:
            member.nickname = request_change_profile.nickname
            update_fields.append('nickname')
        if request_change_profile.profile_image:
            client = boto3.client(
                's3',
                region_name='ap-northeast-2',
                aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
                config=Config(signature_version='s3v4')
            )
            response = generate_pre_signed_url_info(
                client,
                settings.AWS_S3_BUCKET_NAME,
                request_change_profile.profile_image.name,
                'member-profile-image',
                member.id,
            )
            upload_file_to_pre_signed_url(
                response['url'],
                response['fields'],
                request_change_profile.profile_image.read(),
            )
            member.profile_image_url = response['url'] + response['fields']['key']
            update_fields.append('profile_image_url')
        member.save(update_fields=update_fields)
        profile_data = get_member_profile(member.id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=ProfileData(
                    id=profile_data['id'],
                    nickname=profile_data['nickname'],
                    profile_image=profile_data['profile_image'],
                    subscribed_map_count=profile_data['subscribed_map_count'],
                ).model_dump(),
            ).model_dump(),
            status=200,
        )
