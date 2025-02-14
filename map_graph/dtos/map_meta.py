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
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    width: float
    height: float
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
        min_position_x_node = min(nodes, key=lambda node: node.position_x, default=None)
        min_position_y_node = min(nodes, key=lambda node: node.position_y, default=None)
        max_position_x_node = max(nodes, key=lambda node: node.position_x + node.width, default=None)
        max_position_y_node = max(nodes, key=lambda node: node.position_y + node.height, default=None)
        min_x = getattr(min_position_x_node, 'position_x', 0)
        max_x = getattr(max_position_x_node, 'position_x', 0) + max_position_x_node.width
        min_y = getattr(min_position_y_node, 'position_y', 0)
        max_y = getattr(max_position_y_node, 'position_y', 0) + max_position_y_node.height

        width = abs(max_x - min_x)
        height = abs(max_y - min_y)

        if not start_date:
            learning_period = None
        else:
            learning_period = MapLearningPeriodDTO(
                start_date=start_date,
                days=(datetime.now().date() - start_date).days + 1,
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
                min_x=min_x,
                max_x=max_x,
                min_y=min_y,
                max_y=max_y,
                width=width,
                height=height,
                grid_size=20,
            ),
            theme=MapThemeDTO(),
            version=map_obj.updated_at.strftime("%Y%m%d%H%M%S"),
        )
