from typing import (
    Literal,
    Set,
)

from map.models import Arrow
from pydantic import BaseModel


class GraphArrow(BaseModel):
    id: int
    start_node_id: int
    end_node_id: int
    active_rule_id: int
    status: Literal['completed', 'locked'] = 'locked'

    @classmethod
    def from_arrow(
            cls,
            arrow: Arrow,
            completed_arrow_ids: Set[int],
    ) -> 'GraphArrow':
        if arrow.id in completed_arrow_ids:
            status = 'completed'
        else:
            status = 'locked'

        return cls(
            id=arrow.id,
            start_node_id=arrow.start_node_id,
            end_node_id=arrow.node_complete_rule.node_id,
            active_rule_id=arrow.node_complete_rule_id,
            status=status,
        )
