from typing import (
    List,
    Optional,
)

from map.exceptions import MapNotFoundException
from map.models import Map, Node, NodeCompletedHistory
from map_graph.dtos.graph_node import GraphNode


class MapGraphService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

    def get_nodes(self, map_id: int) -> List[GraphNode]:
        try:
            map_obj = Map.objects.get(
                id=map_id,
                is_deleted=False
            )
            if map_obj.is_private and map_obj.created_by_id != self.member_id:
                raise Map.DoesNotExist()
            # 맵에 속한 노드들을 가져옵니다.
            nodes = Node.objects.filter(
                map_id=map_id,
                is_deleted=False,
            ).select_related(
                'map',
            )
            # 완료된 노드들의 id를 저장합니다.
            completed_node_ids = {
                completed_node.id
                for completed_node in self.get_completed_nodes(map_id)
            }
            return [
                GraphNode.from_node(
                    node,
                    completed_node_ids,
                    {},
                )
                for node in nodes
            ]
        except Map.DoesNotExist:
            raise MapNotFoundException()

    def get_completed_nodes(self, map_id: int) -> List[GraphNode]:
        if not self.member_id:
            return []
        completed_histories = NodeCompletedHistory.objects.filter(
            map_id=map_id,
            member_id=self.member_id,
        ).select_related(
            'node__map',
        ).order_by(
            'completed_at',
        )
        completed_nodes_dict = {
            history.node.id: history.node
            for history in completed_histories
        }
        return [
            GraphNode.from_node(
                node,
                set(completed_nodes_dict.keys()),
                {},
            )
            for node in completed_nodes_dict.values()
        ]
