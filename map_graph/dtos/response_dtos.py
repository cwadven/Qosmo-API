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
