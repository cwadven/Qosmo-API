from datetime import datetime
from pydantic import BaseModel, Field
from common.dtos.response_dtos import BaseFormatResponse


class NormalLoginResponse(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class SocialLoginResponse(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class GuestTokenGetOrCreateResponse(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class ProfileData(BaseModel):
    id: int
    nickname: str
    profile_image: str | None
    subscribed_map_count: int
