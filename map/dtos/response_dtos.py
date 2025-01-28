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


class MapDetailRecentActivatedNodeDTO(BaseModel):
    id: int
    name: str
    activated_at: datetime


class MapDetailProgressDTO(BaseModel):
    completed_node_count: int
    total_node_count: int
    percentage: int
    recent_activated_nodes: List[MapDetailRecentActivatedNodeDTO]

    @staticmethod
    def from_map(map_obj: 'Map') -> 'MapDetailProgressDTO':
        # TODO: 실제 진행 상황 계산 로직 구현
        return MapDetailProgressDTO(
            completed_node_count=0,
            total_node_count=map_obj.nodes.count(),
            percentage=0,
            recent_activated_nodes=[]
        )


class MapDetailDTO(BaseModel):
    id: int
    name: str
    description: str
    subscriber_count: int
    view_count: int
    is_subscribed: bool
    icon_image: str
    background_image: str
    created_by: MapListCreatedBy
    progress: Optional[MapDetailProgressDTO]
    created_at: datetime

    @staticmethod
    def from_entity(map_obj: 'Map', progress: MapDetailProgressDTO, is_subscribed: bool = False) -> 'MapDetailDTO':
        return MapDetailDTO(
            id=map_obj.id,
            name=map_obj.name,
            description=map_obj.description,
            subscriber_count=map_obj.subscriber_count,
            view_count=map_obj.view_count,
            is_subscribed=is_subscribed,
            icon_image=map_obj.icon_image,
            background_image=map_obj.background_image,
            created_by=MapListCreatedBy.from_entity(map_obj.created_by),
            progress=progress,
            created_at=map_obj.created_at
        )
