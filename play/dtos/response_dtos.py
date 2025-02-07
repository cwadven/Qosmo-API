from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from play.consts import MapPlayMemberRole, MapPlayMemberDeactivateReason


class MapPlayDTO(BaseModel):
    id: int
    map_id: int
    title: str
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, map_play):
        return cls(
            id=map_play.id,
            map_id=map_play.map_id,
            title=map_play.title,
            created_by_id=map_play.created_by_id,
            created_at=map_play.created_at,
            updated_at=map_play.updated_at,
        )


class MapPlayMemberDTO(BaseModel):
    id: int
    map_play_id: int
    member_id: int
    role: MapPlayMemberRole
    deactivated: bool
    deactivated_reason: Optional[MapPlayMemberDeactivateReason]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, member):
        return cls(
            id=member.id,
            map_play_id=member.map_play_id,
            member_id=member.member_id,
            role=member.role,
            deactivated=member.deactivated,
            deactivated_reason=member.deactivated_reason,
            created_at=member.created_at,
            updated_at=member.updated_at,
        )


class MapPlayInviteCodeDTO(BaseModel):
    id: int
    map_play_id: int
    code: str
    created_by_id: int
    max_uses: Optional[int]
    current_uses: int
    expired_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, invite_code):
        return cls(
            id=invite_code.id,
            map_play_id=invite_code.map_play_id,
            code=invite_code.code,
            created_by_id=invite_code.created_by_id,
            max_uses=invite_code.max_uses,
            current_uses=invite_code.current_uses,
            expired_at=invite_code.expired_at,
            is_active=invite_code.is_active,
            created_at=invite_code.created_at,
            updated_at=invite_code.updated_at,
        )


class InviteCodeStatusDTO(BaseModel):
    is_active: bool
    is_expired: bool
    is_full: bool
    current_uses: int
    max_uses: Optional[int]
    expired_at: Optional[datetime] 