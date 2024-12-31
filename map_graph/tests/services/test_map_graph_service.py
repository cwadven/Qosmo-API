from django.test import TestCase
from map.exceptions import MapNotFoundException
from map.models import (
    Map,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory,
)
from map_graph.dtos.graph_arrow import GraphArrow
from map_graph.services.map_graph_service import MapGraphService, get_start_node_ids_by_end_node_id
from member.models import Member


class MapGraphServiceTest(TestCase):
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
        self.nodes = []
        for i in range(4):
            self.nodes.append(
                Node.objects.create(
                    map=self.map,
                    name=f'Test Node {i}',
                    title=f'Test Title {i}',
                    description=f'Test Description {i}',
                    position_x=i * 100,
                    position_y=i * 100,
                    is_active=True,
                )
            )

        # Given: 첫 번째 Node 완료 처리를 위한 Rule 생성
        self.node_complete_rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[0],
        )

        # Given: 첫 번째 Node 완료 처리
        NodeCompletedHistory.objects.create(
            map=self.map,
            node=self.nodes[0],
            member=self.member,
            node_complete_rule=self.node_complete_rule,
        )

    def test_should_return_nodes_when_get_nodes(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # When: Node 목록 조회
        nodes = service.get_nodes(self.map.id)

        # Then: Node 목록이 반환되어야 함
        self.assertEqual(len(nodes), 4)
        # Then: 첫 번째 노드는 completed 상태여야 함
        self.assertEqual(nodes[0].status, 'completed')
        # Then: 나머지 노드들은 locked 상태여야 함
        self.assertEqual(nodes[1].status, 'locked')
        self.assertEqual(nodes[2].status, 'locked')

    def test_should_return_completed_nodes_when_get_completed_nodes(self):
        # Given: 회원으로 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # When: 완료된 Node 목록 조회
        completed_nodes = service.get_completed_nodes(self.map.id)

        # Then: 완료된 Node가 반환되어야 함
        self.assertEqual(len(completed_nodes), 1)
        self.assertEqual(completed_nodes[0].id, self.nodes[0].id)
        self.assertEqual(completed_nodes[0].status, 'completed')

    def test_should_return_empty_list_when_get_completed_nodes_without_member(self):
        # Given: 비회원으로 서비스 초기화
        service = MapGraphService()

        # When: 완료된 Node 목록 조회
        completed_nodes = service.get_completed_nodes(self.map.id)

        # Then: 빈 리스트가 반환되어야 함
        self.assertEqual(len(completed_nodes), 0)

    def test_should_raise_exception_when_get_nodes_with_invalid_map_id(self):
        # Given: 서비스 초기화
        service = MapGraphService()

        # When & Then: 존재하지 않는 Map ID로 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_nodes(99999)

    def test_should_raise_exception_when_get_nodes_with_private_map(self):
        # Given: 비공개 Map 생성
        private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            created_by=self.member,
            is_private=True,
        )
        service = MapGraphService()

        # When & Then: 다른 사용자가 비공개 Map 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_nodes(private_map.id)

        # When: 소유자가 비공개 Map 조회
        service = MapGraphService(member_id=self.member.id)
        nodes = service.get_nodes(private_map.id)

        # Then: 정상적으로 조회되어야 함
        self.assertEqual(len(nodes), 0)

    def test_should_return_empty_dict_when_no_arrows(self):
        # When: 화살표가 없을 때 매핑 생성
        result = get_start_node_ids_by_end_node_id([])
        
        # Then: 빈 딕셔너리가 반환되어야 함
        self.assertEqual(len(result), 0)

    def test_should_return_correct_mapping_with_single_arrow(self):
        # Given: 단일 화살표 생성
        arrow = GraphArrow(
            id=1,
            start_node_id=self.nodes[0].id,
            end_node_id=self.nodes[1].id,
        )
        
        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id([arrow])
        
        # Then: 올바른 매핑이 생성되어야 함
        self.assertEqual(len(result), 1)
        self.assertEqual(result[self.nodes[1].id], {self.nodes[0].id})

    def test_should_return_correct_mapping_with_multiple_arrows_to_same_end_node(self):
        # Given: 같은 end_node를 가리키는 여러 화살표 생성
        arrows = [
            GraphArrow(
                id=1,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[2].id,
            ),
            GraphArrow(
                id=2,
                start_node_id=self.nodes[1].id,
                end_node_id=self.nodes[2].id,
            ),
        ]
        
        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id(arrows)
        
        # Then: 올바른 매핑이 생성되어야 함
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[self.nodes[2].id],
            {self.nodes[0].id, self.nodes[1].id}
        )

    def test_should_ignore_self_referencing_arrows(self):
        # Given: self-referencing 화살표 생성
        arrow = GraphArrow(
            id=1,
            start_node_id=self.nodes[0].id,
            end_node_id=self.nodes[0].id,  # 같은 노드를 가리킴
        )
        
        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id([arrow])
        
        # Then: self-referencing 화살표는 무시되어야 함
        self.assertEqual(len(result), 0)

    def test_should_handle_complex_arrow_relationships(self):
        # Given: 복잡한 화살표 관계 생성
        arrows = [
            # 정상적인 화살표들
            GraphArrow(
                id=1,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[1].id,
            ),
            GraphArrow(
                id=2,
                start_node_id=self.nodes[1].id,
                end_node_id=self.nodes[2].id,
            ),
            # 같은 end_node를 가리키는 화살표
            GraphArrow(
                id=3,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[2].id,
            ),
            # self-referencing 화살표
            GraphArrow(
                id=4,
                start_node_id=self.nodes[3].id,
                end_node_id=self.nodes[3].id,
            ),
        ]
        
        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id(arrows)
        
        # Then: 올바른 매핑이 생성되어야 함
        self.assertEqual(len(result), 2)  # node1, node2를 가리키는 매핑만 있어야 함
        self.assertEqual(result[self.nodes[1].id], {self.nodes[0].id})
        self.assertEqual(
            result[self.nodes[2].id],
            {self.nodes[0].id, self.nodes[1].id}
        )
