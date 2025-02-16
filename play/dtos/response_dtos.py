from typing import (
    List,
    Optional,
)
from pydantic import BaseModel
from datetime import datetime

from map.models import NodeCompletedHistory
from play.consts import (
    MapPlayMemberDeactivateReason,
    MapPlayMemberRole,
)
from play.models import MapPlayMember


class MapPlayDTO(BaseModel):
    id: int
    map_play_id: int
    map_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_map_play_member(cls, map_play_member: MapPlayMember):
        return cls(
            id=map_play_member.id,
            map_play_id=map_play_member.map_play_id,
            map_id=map_play_member.map_play.map_id,
            title=map_play_member.map_play.title,
            created_at=map_play_member.created_at,
            updated_at=map_play_member.updated_at,
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


class MapPlayRecentActivatedNode(BaseModel):
    node_id: int
    node_name: str
    activated_at: datetime


class MapPlayListDTO(BaseModel):
    id: int
    title: str
    role: MapPlayMemberRole
    joined_at: datetime
    completed_node_count: int
    recent_activated_nodes: List[MapPlayRecentActivatedNode]

    @classmethod
    def from_map_play_member(
            cls,
            map_play_member: MapPlayMember,
            completed_node_count: int,
            recent_activated_nodes: List[MapPlayRecentActivatedNode]
    ):
        return cls(
            id=map_play_member.id,
            title=map_play_member.map_play.title,
            role=map_play_member.role,
            joined_at=map_play_member.created_at,
            completed_node_count=completed_node_count,
            recent_activated_nodes=recent_activated_nodes,
        )
