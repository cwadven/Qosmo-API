from datetime import datetime
from typing import (
    List,
    Optional,
)

from map.models import Map
from member.models import Member
from pydantic import BaseModel


class MapListCreatedBy(BaseModel):
    id: int
    nickname: str

    @staticmethod
    def from_entity(member: 'Member') -> 'MapListCreatedBy':
        return MapListCreatedBy(
            id=member.id,
            nickname=member.nickname
        )


class MapListItemDTO(BaseModel):
    id: int
    name: str
    description: str
    icon_image: str
    background_image: str
    subscriber_count: int
    view_count: int
    is_subscribed: bool
    created_by: MapListCreatedBy
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(_map: 'Map', is_subscribed: bool = False) -> 'MapListItemDTO':
        return MapListItemDTO(
            id=_map.id,
            name=_map.name,
            description=_map.description,
            icon_image=_map.icon_image,
            background_image=_map.background_image,
            subscriber_count=_map.subscriber_count,
            view_count=_map.view_count,
            is_subscribed=is_subscribed,
            created_by=MapListCreatedBy.from_entity(_map.created_by),
            created_at=_map.created_at,
            updated_at=_map.updated_at
        )


class MapListResponseDTO(BaseModel):
    maps: List[MapListItemDTO]
    next_cursor: Optional[str]
    has_more: bool
