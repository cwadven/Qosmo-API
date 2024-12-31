from datetime import datetime
from typing import Dict, List, Optional

from map.models import Map, Node
from pydantic import BaseModel

from map_graph.dtos.graph_node import GraphNode


class MapThemeDTO(BaseModel):
    background_color: str = "#f8f9fa"
    grid_color: str = "#ddd"
    node: Dict = {
        "completed": {
            "background": "#FFFFFF",
            "border": "#4CAF50",
            "text": "#4CAF50",
            "icon": "checkmark-circle"
        },
        "in_progress": {
            "background": "#FFFFFF",
            "border": "#2196F3",
            "text": "#2196F3",
            "icon": "play-circle"
        },
        "locked": {
            "background": "#FFFFFF",
            "border": "#666666",
            "text": "#666666",
            "icon": "lock-closed"
        }
    }
    arrow: Dict = {
        "completed": "#4CAF50",
        "locked": "#666666"
    }


class MapLayoutDTO(BaseModel):
    width: int
    height: int
    grid_size: int = 20


class MapLearningPeriodDTO(BaseModel):
    start_date: datetime
    days: int = 60


class MapStatsDTO(BaseModel):
    total_nodes: int
    completed_nodes: int
    learning_period: Optional[MapLearningPeriodDTO]
    total_questions: int = 0
    solved_questions: int = 0


class MapMetaDTO(BaseModel):
    id: int
    title: str
    description: str
    stats: MapStatsDTO
    layout: MapLayoutDTO
    theme: MapThemeDTO
    version: str

    @classmethod
    def from_map(
            cls,
            map_obj: Map,
            nodes: List[Node],
            completed_nodes: List[GraphNode],
            start_date: Optional[datetime] = None,
    ) -> 'MapMetaDTO':
        # 레이아웃 계산
        max_x = max((node.position_x for node in nodes), default=0)
        max_y = max((node.position_y for node in nodes), default=0)
        width = max(3000, int(max_x * 1.2))  # 여유 공간 20% 추가
        height = max(3000, int(max_y * 1.2))

        if not start_date:
            learning_period = None
        else:
            learning_period = MapLearningPeriodDTO(
                start_date=start_date,
                days=60,
            )

        return cls(
            id=map_obj.id,
            title=map_obj.name,
            description=map_obj.description,
            stats=MapStatsDTO(
                total_nodes=len(nodes),
                completed_nodes=len(completed_nodes),
                learning_period=learning_period,
            ),
            layout=MapLayoutDTO(
                width=width,
                height=height,
                grid_size=20,
            ),
            theme=MapThemeDTO(),
            version=map_obj.updated_at.strftime("%Y%m%d%H%M%S"),
        )
