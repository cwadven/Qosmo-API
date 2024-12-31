from typing import (
    Dict,
    List,
    Optional,
    Set,
)

from map.exceptions import MapNotFoundException
from map.models import (
    Arrow,
    Map,
    Node,
    NodeCompletedHistory,
)
from map_graph.dtos.graph_arrow import GraphArrow
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

            # 화살표 데이터를 가져와서 시작 노드 매핑을 생성합니다.
            arrows = Arrow.objects.filter(
                map_id=map_id,
                is_deleted=False,
            ).select_related(
                'start_node',
                'end_node',
            )
            start_node_ids_by_end_node_id = get_start_node_ids_by_end_node_id(arrows)

            # 완료된 노드들의 id를 저장합니다.
            completed_node_ids = {
                completed_node.id
                for completed_node in self.get_completed_nodes(map_id)
            }

            return [
                GraphNode.from_node(
                    node,
                    completed_node_ids,
                    start_node_ids_by_end_node_id,
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


def get_start_node_ids_by_end_node_id(arrows: List[GraphArrow]) -> Dict[int, Set[int]]:
    """
    화살표 목록에서 end_node_id를 키로 하고 해당 end_node로 향하는 모든 start_node_id를 값으로 하는 딕셔너리를 반환합니다.
    self-referencing arrow(시작과 끝이 같은 화살표)는 무시됩니다.
    """
    start_node_ids_by_end_node_id: Dict[int, Set[int]] = {}

    for arrow in arrows:
        if arrow.start_node_id == arrow.end_node_id:
            continue

        if arrow.end_node_id not in start_node_ids_by_end_node_id:
            start_node_ids_by_end_node_id[arrow.end_node_id] = set()
        start_node_ids_by_end_node_id[arrow.end_node_id].add(arrow.start_node_id)

    return start_node_ids_by_end_node_id
