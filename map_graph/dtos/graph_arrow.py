from typing import Dict, List, Set

from map.models import Arrow
from pydantic import BaseModel


class GraphArrow(BaseModel):
    id: int
    start_node_id: int
    end_node_id: int

    @classmethod
    def from_arrow(cls, arrow: Arrow) -> 'GraphArrow':
        return cls(
            id=arrow.id,
            start_node_id=arrow.start_node_id,
            end_node_id=arrow.end_node_id,
        )
