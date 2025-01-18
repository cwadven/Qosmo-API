from typing import (
    Dict,
    Literal,
    Set,
)

from map.models import Node
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: int
    name: str
    position_x: float
    position_y: float
    width: float
    height: float
    status: Literal['completed', 'in_progress', 'locked', 'deactivated'] = 'locked'

    @classmethod
    def from_node(
            cls,
            node: Node,
            completed_node_ids: Set[int],
            start_node_ids_by_end_node_id: Dict[int, Set[int]],
    ) -> 'GraphNode':
        return cls(
            id=node.id,
            name=node.name,
            position_x=node.position_x,
            position_y=node.position_y,
            width=node.width,
            height=node.height,
            status=cls.get_status(
                node,
                completed_node_ids,
                start_node_ids_by_end_node_id,
            ),
        )

    @classmethod
    def get_status(
            cls,
            node: Node,
            completed_node_ids: Set[int],
            start_node_ids_by_end_node_id: Dict[int, Set[int]],
    ):
        if not node.is_active:
            return 'deactivated'
        if node.id in completed_node_ids:
            return 'completed'
        start_node_ids = start_node_ids_by_end_node_id.get(node.id, set())
        # 처음 Node
        if not start_node_ids:
            return 'in_progress'
        # 중간 Node
        if start_node_ids & completed_node_ids:
            return 'in_progress'
        else:
            return 'locked'
