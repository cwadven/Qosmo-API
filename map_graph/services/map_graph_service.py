from typing import (
    Dict,
    List,
    Optional,
    Set,
)

from django.utils import timezone

from map.models import (
    Arrow,
    NodeCompleteRule, ArrowProgress,
)
from map_graph.dtos.graph_arrow import GraphArrow
from map_graph.dtos.graph_node import GraphNode
from map_graph.dtos.response_dtos import NodeCompleteRuleDTO
from map_graph.dtos.map_meta import MapMetaDTO
from node.services.node_services import (
    get_nodes_by_map_id,
)
from play.models import MapPlayMember
from subscription.models import MapSubscription
from play.services import MapPlayService


class MapGraphService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id
        self.map_play_service = MapPlayService()

    def get_nodes(self, map_id: int, map_play_member_id: Optional[int] = None) -> List[GraphNode]:
        # Map과 MapPlayMember 접근 권한 검증
        self.map_play_service.validate_map_and_play_member_access(map_id, self.member_id, map_play_member_id)

        # 맵에 속한 노드들을 가져옵니다.
        nodes = get_nodes_by_map_id(map_id)

        # 화살표 데이터를 가져와서 시작 노드 매핑을 생성합니다.
        arrows = Arrow.objects.filter(
            map_id=map_id,
            is_deleted=False,
        ).select_related(
            'start_node',
            'node_complete_rule__node',
        )
        start_node_ids_by_end_node_id = get_start_node_ids_by_end_node_id(arrows)

        # 완료된 노드들의 id를 저장합니다.
        completed_node_ids = {
            completed_node.id
            for completed_node in self.get_map_play_member_completed_nodes(map_play_member_id)
        }

        return [
            GraphNode.from_node(
                node,
                completed_node_ids,
                start_node_ids_by_end_node_id,
            )
            for node in nodes
        ]

    def get_map_play_member_completed_nodes(self, map_play_member_id: Optional[int] = None) -> List[GraphNode]:
        """
        특정 맵 플레이 멤버가 완료한 노드들을 GraphNode 형태로 반환합니다.
        """
        if not map_play_member_id:
            return []
        completed_histories = self.map_play_service.get_map_play_completed_node_histories(
            self.map_play_service._get_map_play_member_by_id(map_play_member_id).map_play_id
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

    def get_arrows(self, map_id: int, map_play_member_id: Optional[int] = None) -> List[GraphArrow]:
        # Map과 MapPlayMember 접근 권한 검증
        self.map_play_service.validate_map_and_play_member_access(map_id, self.member_id, map_play_member_id)

        # 화살표 데이터를 가져옵니다.
        arrows = Arrow.objects.filter(
            map_id=map_id,
            is_deleted=False,
        )
        completed_arrow_ids = set(
            ArrowProgress.objects.filter(
                arrow_id__in=arrows.values_list('id', flat=True),
                is_resolved=True,
            ).values_list(
                'arrow_id',
                flat=True,
            )
        )
        return [
            GraphArrow.from_arrow(
                arrow,
                completed_arrow_ids,
            )
            for arrow in arrows
        ]

    def get_node_complete_rules(self, map_id: int) -> List[NodeCompleteRuleDTO]:
        # Map 접근 권한 검증
        self.map_play_service.validate_map_access(map_id, self.member_id)

        rules = NodeCompleteRule.objects.filter(
            map_id=map_id,
            is_deleted=False,
        ).select_related(
            'node',
        )
        return [
            NodeCompleteRuleDTO.from_rule(rule)
            for rule in rules
        ]

    def get_map_meta(self, map_id: int, map_play_member_id: Optional[int] = None) -> MapMetaDTO:
        # Map과 MapPlayMember 접근 권한 검증
        map_obj = self.map_play_service.validate_map_and_play_member_access(map_id, self.member_id, map_play_member_id)

        nodes = list(get_nodes_by_map_id(map_id))
        completed_nodes = self.get_map_play_member_completed_nodes(map_play_member_id)

        start_date = None
        if map_play_member_id:
            try:
                joined_map_play = MapPlayMember.objects.get(
                    id=map_play_member_id,
                    deactivated=False,
                )
                # UTC 시간을 현재 timezone으로 변환 후 날짜 추출
                start_date = timezone.localtime(joined_map_play.created_at).date()
            except MapPlayMember.DoesNotExist:
                pass
        return MapMetaDTO.from_map(
            map_obj=map_obj,
            nodes=nodes,
            completed_nodes=completed_nodes,
            start_date=start_date,
        )


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
