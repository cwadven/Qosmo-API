from typing import (
    Dict,
    List,
)
from collections import (
    defaultdict,
    deque,
)

from django.db import transaction
from django.utils import timezone

from map.models.arrow import Arrow
from map.models.arrow_progress import ArrowProgress
from map.models.node import Node
from map.models.node_history import NodeCompletedHistory
from map.models.node_rule import NodeCompleteRule
from question.dtos.node_completion import NodeCompletionResultDto


class NodeCompletionService:
    def __init__(self, member_id: int):
        self.member_id = member_id

    @transaction.atomic
    def process_nodes_completion(self, nodes: List[Node]) -> NodeCompletionResultDto:
        """
        주어진 노드들부터 시작하여 연쇄적으로 해금 가능한 모든 노드들을 처리합니다.
        """
        if not nodes:
            return NodeCompletionResultDto(
                new_arrow_progresses=[],
                new_completed_node_histories=[]
            )

        map_id = nodes[0].map_id  # 모든 노드는 같은 map에 속한다고 가정
        map_data = self._fetch_map_data(map_id)

        new_arrow_progresses = []
        new_completed_node_histories = []
        now = timezone.now()

        nodes_to_process = deque(node.id for node in nodes)
        processed_nodes = set()

        while nodes_to_process:
            current_node_id = nodes_to_process.popleft()

            if current_node_id in processed_nodes:
                continue

            processed_nodes.add(current_node_id)

            # 현재 노드에서 출발하는 Arrow들에 대한 ArrowProgress 생성
            outgoing_arrows = map_data['arrows_by_start_node_id'].get(current_node_id, [])
            for arrow in outgoing_arrows:
                if arrow.id not in map_data['completed_arrows']:
                    new_arrow_progresses.append(
                        ArrowProgress(
                            map_id=map_data['map_id'],
                            arrow=arrow,
                            member_id=self.member_id,
                            is_resolved=True,
                            resolved_at=now
                        )
                    )
                    map_data['completed_arrows'].add(arrow.id)

            # 새로 완료된 Arrow로 인해 해금 가능한 Node 찾기
            going_to_completed_nodes = self._find_going_to_completed_nodes(map_data)

            # 해금된 Node들 처리
            for going_to_completed_node_id, rule in going_to_completed_nodes:
                new_completed_node_histories.append(
                    NodeCompletedHistory(
                        map_id=map_data['map_id'],
                        node_id=going_to_completed_node_id,
                        member_id=self.member_id,
                        node_complete_rule=rule
                    )
                )
                map_data['completed_node_ids'].add(going_to_completed_node_id)
                map_data['completed_node_rule_ids'].add(rule.id)
                nodes_to_process.append(going_to_completed_node_id)

        # 모아둔 데이터 한 번에 생성
        if new_arrow_progresses:
            ArrowProgress.objects.bulk_create(new_arrow_progresses)
        if new_completed_node_histories:
            NodeCompletedHistory.objects.bulk_create(new_completed_node_histories)

        return NodeCompletionResultDto(
            new_arrow_progresses=new_arrow_progresses,
            new_completed_node_histories=new_completed_node_histories
        )

    def _fetch_map_data(self, map_id: int) -> Dict:
        """
        필요한 모든 데이터를 미리 가져옵니다.
        """
        # Arrow와 연결된 Node들 가져오기
        arrows = Arrow.objects.filter(
            map_id=map_id,
            is_deleted=False
        ).select_related('start_node', 'end_node', 'node_complete_rule')

        # NodeCompleteRule 가져오기
        rules = NodeCompleteRule.objects.filter(
            map_id=map_id,
            is_deleted=False
        )

        # 기존 ArrowProgress 가져오기
        existing_progresses = ArrowProgress.objects.filter(
            map_id=map_id,
            member_id=self.member_id,
            is_resolved=True
        )

        # 기존 NodeCompletedHistory 가져오기 (node_complete_rule_id도 함께 가져옴)
        completed_histories = NodeCompletedHistory.objects.filter(
            map_id=map_id,
            member_id=self.member_id
        ).values_list('node_id', 'node_complete_rule_id')

        # rule별 arrow 매핑 구성
        arrows_by_rule_id = {}
        for arrow in arrows:
            rule_id = arrow.node_complete_rule_id
            if rule_id not in arrows_by_rule_id:
                arrows_by_rule_id[rule_id] = set()
            arrows_by_rule_id[rule_id].add(arrow)

        # rules_by_node_id 구성
        rules_by_node_id = defaultdict(list)
        for rule in rules:
            rules_by_node_id[rule.node_id].append(rule)

        # arrows_by_start_node_id 구성
        arrows_by_start_node_id = {}
        for arrow in arrows:
            if arrow.start_node_id not in arrows_by_start_node_id:
                arrows_by_start_node_id[arrow.start_node_id] = []
            arrows_by_start_node_id[arrow.start_node_id].append(arrow)

        # 데이터 구조화
        return {
            'map_id': map_id,
            'arrows_by_start_node_id': arrows_by_start_node_id,
            'rules_by_node_id': rules_by_node_id,
            'arrows_by_rule_id': arrows_by_rule_id,
            'completed_arrows': {p.arrow_id for p in existing_progresses},
            'completed_node_ids': {node_id for node_id, _ in completed_histories},
            'completed_node_rule_ids': {rule_id for _, rule_id in completed_histories},
        }

    @staticmethod
    def _find_going_to_completed_nodes(map_data: Dict) -> List[tuple[int, NodeCompleteRule]]:
        """
        Completed 가 될 수 있는 조건이 충족된 Node들을 찾습니다.
        하나의 Node 가 해결 되면 여러 규칙으로 해금될 수 있으며,
        이미 해금된 규칙은 다시 생성하지 않습니다.
        """
        going_to_completed = []
        for node_id, node_rules in map_data['rules_by_node_id'].items():
            # 노드의 모든 규칙을 체크
            for rule in node_rules:
                # 이미 해당 규칙으로 해금된 이력이 있다면 스킵
                if rule.id in map_data['completed_node_rule_ids']:
                    continue

                rule_arrows = map_data['arrows_by_rule_id'].get(rule.id, [])
                if all(arrow.id in map_data['completed_arrows'] for arrow in rule_arrows):
                    going_to_completed.append((node_id, rule))
        
        return going_to_completed
