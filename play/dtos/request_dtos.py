from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

from play.consts import MapPlayMemberRole


class CreateMapPlayRequestDTO(BaseModel):
    title: str = Field(..., description="플레이 제목")

    @classmethod
    def of(cls, request):
        return cls(**request.data)


class CreateInviteCodeRequestDTO(BaseModel):
    max_uses: Optional[int] = Field(None, description="최대 사용 횟수")
    expired_at: Optional[datetime] = Field(None, description="만료일시")

    @classmethod
    def of(cls, request):
        return cls(**request.data)


class ChangeMemberRoleRequestDTO(BaseModel):
    new_role: MapPlayMemberRole = Field(..., description="새로운 역할")
    reason: Optional[str] = Field(None, description="변경 사유")

    @classmethod
    def of(cls, request):
        return cls(**request.data)


class BanMemberRequestDTO(BaseModel):
    banned_reason: str = Field(..., description="추방 사유")
    invite_code_id: Optional[int] = Field(None, description="초대 코드 ID")

    @classmethod
    def of(cls, request):
        return cls(**request.data) 