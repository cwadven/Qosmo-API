from typing import List

from map.models import NodeCompleteRule
from map_graph.dtos.graph_node import GraphNode
from pydantic import BaseModel


class NodeGraphDTO(BaseModel):
    id: int
    name: str
    position_x: float
    position_y: float
    status: str

    @staticmethod
    def from_graph_node(node: GraphNode) -> 'NodeGraphDTO':
        return NodeGraphDTO(
            id=node.id,
            name=node.name,
            position_x=node.position_x,
            position_y=node.position_y,
            status=node.status
        )


class NodeCompleteRuleDTO(BaseModel):
    id: int
    name: str
    target_nodes: List[int]

    @classmethod
    def from_rule(cls, rule: NodeCompleteRule) -> 'NodeCompleteRuleDTO':
        return cls(
            id=rule.id,
            name=rule.name,
            target_nodes=[rule.node_id],
        )
