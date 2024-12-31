from unittest.mock import patch

from django.test import TestCase
from map.models import (
    Arrow,
    Map,
    Node,
    NodeCompleteRule,
)
from map_graph.dtos.graph_node import GraphNode
from member.models import Member


class GraphNodeTest(TestCase):
    def setUp(self):
        # Given: 테스트 사용자 생성
        self.member = Member.objects.create(
            username='test_user',
            nickname='테스트 유저',
        )

        # Given: 테스트 Map 생성
        self.map = Map.objects.create(
            name='Test Map',
            description='Test Description',
            created_by=self.member,
            is_private=False,
        )

        # Given: 테스트 Node 생성
        self.node = Node.objects.create(
            map=self.map,
            name='Test Node',
            title='Test Title',
            description='Test Description',
            position_x=100.0,
            position_y=200.0,
            is_active=True,
        )

        # Given: 다른 테스트 Node 생성 (Arrow 테스트용)
        self.end_node = Node.objects.create(
            map=self.map,
            name='End Node',
            title='End Title',
            description='End Description',
            position_x=300.0,
            position_y=400.0,
            is_active=True,
        )

        self.node_complete_rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.end_node,
        )

        # Given: Arrow 생성
        self.arrow = Arrow.objects.create(
            map=self.map,
            start_node=self.node,
            end_node=self.end_node,
            node_complete_rule_id=self.node_complete_rule.id,
        )

    @patch.object(GraphNode, 'get_status')
    def test_should_create_graph_node_from_node(self, mock_get_status):
        # Given: get_status 모킹
        mock_get_status.return_value = 'locked'
        completed_node_ids = set()
        start_node_ids_by_end_node_id = {}

        # When: Node로부터 GraphNode 생성
        graph_node = GraphNode.from_node(
            self.node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

        # Then: GraphNode가 올바르게 생성되어야 함
        self.assertEqual(graph_node.id, self.node.id)
        self.assertEqual(graph_node.name, self.node.name)
        self.assertEqual(graph_node.position_x, self.node.position_x)
        self.assertEqual(graph_node.position_y, self.node.position_y)
        self.assertEqual(graph_node.status, 'locked')

        # Then: get_status가 올바른 인자로 호출되어야 함
        mock_get_status.assert_called_once_with(
            self.node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

    def test_should_return_deactivated_status_from_get_status(self):
        # Given: 테스트 데이터 설정
        completed_node_ids = {self.node.id}
        start_node_ids_by_end_node_id = {
            self.end_node.id: {self.node.id}
        }
        # And: 비활성화된 노드
        self.node.is_active = False

        # When: get_status 호출
        status = GraphNode.get_status(
            self.node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

        # Then: 비활성화된 노드는 'deactivated' 상태여야 함
        self.assertEqual(status, 'deactivated')

    def test_should_return_completed_status_from_get_status(self):
        # Given: 테스트 데이터 설정
        completed_node_ids = {self.node.id}
        start_node_ids_by_end_node_id = {
            self.end_node.id: {self.node.id}
        }

        # When: get_status 호출
        status = GraphNode.get_status(
            self.node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

        # Then: 완료된 노드는 'completed' 상태여야 함
        self.assertEqual(status, 'completed')

    def test_should_return_in_progress_status_from_get_status(self):
        # Given: 테스트 데이터 설정
        completed_node_ids = {self.node.id}
        start_node_ids_by_end_node_id = {
            self.end_node.id: {self.node.id}
        }

        # When: get_status 호출
        status = GraphNode.get_status(
            self.end_node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

        # Then: 진행 중인 노드는 'in_progress' 상태여야 함
        self.assertEqual(status, 'in_progress')

    def test_should_return_in_progress_status_when_start_node_from_get_status(self):
        # Given: 시작 노드 처럼 만들기
        completed_node_ids = set()
        start_node_ids_by_end_node_id = {}

        # When: get_status 호출
        status = GraphNode.get_status(
            self.node,
            completed_node_ids,
            start_node_ids_by_end_node_id,
        )

        # Then: 진행 중인 노드는 'in_progress' 상태여야 함
        self.assertEqual(status, 'in_progress')

    def test_should_return_locked_status_from_get_status(self):
        # Given: 테스트 데이터 설정
        start_node_ids_by_end_node_id = {
            self.end_node.id: {self.node.id}
        }

        # When: get_status 호출
        status = GraphNode.get_status(
            self.end_node,
            set(),  # 완료된 노드 없음
            start_node_ids_by_end_node_id,
        )

        # Then: 잠겨 있는 노드는 'locked' 상태여야 함
        self.assertEqual(status, 'locked')
