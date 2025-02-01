from datetime import date
from typing import (
    List,
    Optional, Any,
)

from common.common_consts.common_error_messages import ErrorMessage
from django.http import QueryDict
from pydantic import (
    BaseModel,
    Field,
    field_validator, model_validator,
)

from member.consts import MemberCreationExceptionMessage, NICKNAME_MIN_LENGTH, NICKNAME_MAX_LENGTH
from member.services import check_nickname_valid, check_nickname_exists, check_only_korean_english_alphanumeric


class NormalLoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class SocialLoginRequest(BaseModel):
    token: str = Field(...)
    provider: int = Field(...)


class SocialSignUpJobInfo(BaseModel):
    job_id: int = Field(...)
    start_date: date = Field(...)
    end_date: Optional[date] = Field(...)


class SocialSignUpRequest(BaseModel):
    token: str = Field(description='외부 로그인 토큰')
    provider: int = Field(description='외부 로그인 제공자')
    jobs_info: Optional[List[SocialSignUpJobInfo]] = Field(description='회원 직군 정보')

    @field_validator(
        'jobs_info',
        mode='before'
    )
    def check_jobs_value(cls, v):
        if v is None:
            return None

        if not len(v):
            raise ValueError(ErrorMessage.INVALID_MINIMUM_ITEM_SIZE.label.format(1))

        for job_info in v:
            if set(job_info.keys()) != {'job_id', 'start_date', 'end_date'}:
                raise ValueError(ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label)
        return v

    @classmethod
    def of(cls, request: QueryDict):
        return cls(
            **request
        )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(...)


class SignUpEmailTokenSendRequest(BaseModel):
    email: str = Field(...)
    username: str = Field(...)
    nickname: str = Field(...)
    password2: str = Field(...)


class SignUpEmailTokenValidationEndRequest(BaseModel):
    email: str = Field(...)
    one_time_token: str = Field(...)


class SignUpValidationRequest(BaseModel):
    username: str = Field(...)
    nickname: str = Field(...)
    email: str = Field(...)
    password1: str = Field(...)
    password2: str = Field(...)


class ChangeProfileRequest(BaseModel):
    nickname: Optional[str] = Field(...)
    profile_image: Any = Field(...)

    @field_validator(
        'nickname',
        mode='before'
    )
    def check_nickname(cls, v):
        if v is None:
            return v

        if not check_nickname_valid(v):
            raise ValueError(MemberCreationExceptionMessage.NICKNAME_BLACKLIST.label)
        if check_nickname_exists(v):
            raise ValueError(MemberCreationExceptionMessage.NICKNAME_EXISTS.label)
        if not (NICKNAME_MIN_LENGTH <= len(v) <= NICKNAME_MAX_LENGTH):
            raise ValueError(
                MemberCreationExceptionMessage.NICKNAME_LENGTH_INVALID.label.format(
                    NICKNAME_MIN_LENGTH,
                    NICKNAME_MAX_LENGTH,
                )
            )
        if not check_only_korean_english_alphanumeric(v):
            raise ValueError(MemberCreationExceptionMessage.NICKNAME_REG_EXP_INVALID.label)
        return v

    @field_validator(
        'profile_image',
        mode='before'
    )
    def check_profile_image(cls, v):
        if v is None:
            return v
        if v.content_type not in {'image/png', 'image/webp', 'image/jpeg', 'image/jpg', 'image/gif'}:
            raise ValueError(
                ErrorMessage.INVALID_INPUT_DEPENDENCIES_ERROR.label.format(
                    '이미지 형식은 png, webp, jpeg, jpg, gif 만 가능합니다.',
                )
            )
        return v

    @model_validator(mode='after')
    def check_nickname_and_profile_image(cls, values):
        nickname = values.nickname
        profile_image = values.profile_image

        if nickname is None and not profile_image:
            raise ValueError(
                ErrorMessage.INVALID_INPUT_DEPENDENCIES_ERROR.label.format(
                    'nickname, profile_image 둘중 하나는 필수 입니다.'
                )
            )
        return values
