from django.test import TestCase
from map.exceptions import MapNotFoundException
from map.models import (
    Map,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory,
    Arrow,
)
from map_graph.dtos.graph_arrow import GraphArrow
from map_graph.services.map_graph_service import MapGraphService, get_start_node_ids_by_end_node_id
from member.models import Member
from subscription.models import MapSubscription


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
        node_complete_rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[1],
        )
        arrow = GraphArrow(
            id=1,
            start_node_id=self.nodes[0].id,
            end_node_id=self.nodes[1].id,
            active_rule_id=node_complete_rule.id,
            status='locked',
        )

        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id([arrow])

        # Then: 올바른 매핑이 생성되어야 함
        self.assertEqual(len(result), 1)
        self.assertEqual(result[self.nodes[1].id], {self.nodes[0].id})

    def test_should_return_correct_mapping_with_multiple_arrows_to_same_end_node(self):
        # Given: 같은 end_node를 가리키는 여러 화살표 생성
        node_complete_rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[2],
        )
        arrows = [
            GraphArrow(
                id=1,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[2].id,
                active_rule_id=node_complete_rule.id,
                status='locked',
            ),
            GraphArrow(
                id=2,
                start_node_id=self.nodes[1].id,
                end_node_id=self.nodes[2].id,
                active_rule_id=node_complete_rule.id,
                status='locked',
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
        node_complete_rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[0],
        )
        arrow = GraphArrow(
            id=1,
            start_node_id=self.nodes[0].id,
            end_node_id=self.nodes[0].id,  # 같은 노드를 가리킴
            active_rule_id=node_complete_rule.id,
            status='locked',
        )

        # When: 매핑 생성
        result = get_start_node_ids_by_end_node_id([arrow])

        # Then: self-referencing 화살표는 무시되어야 함
        self.assertEqual(len(result), 0)

    def test_should_handle_complex_arrow_relationships(self):
        # Given: 복잡한 화살표 관계 생성
        node_complete_rule1 = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[1],
        )
        node_complete_rule2 = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[2],
        )
        node_complete_rule3 = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.nodes[3],
        )
        arrows = [
            # 정상적인 화살표들
            GraphArrow(
                id=1,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[1].id,
                active_rule_id=node_complete_rule1.id,
                status='locked',
            ),
            GraphArrow(
                id=2,
                start_node_id=self.nodes[1].id,
                end_node_id=self.nodes[2].id,
                active_rule_id=node_complete_rule2.id,
                status='locked',
            ),
            # 같은 end_node를 가리키는 화살표
            GraphArrow(
                id=3,
                start_node_id=self.nodes[0].id,
                end_node_id=self.nodes[2].id,
                active_rule_id=node_complete_rule2.id,
                status='locked',
            ),
            # self-referencing 화살표
            GraphArrow(
                id=4,
                start_node_id=self.nodes[3].id,
                end_node_id=self.nodes[3].id,
                active_rule_id=node_complete_rule3.id,
                status='locked',
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

    def test_should_return_arrows_when_get_arrows(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # Given: Arrow 생성
        arrow = Arrow.objects.create(
            map=self.map,
            start_node=self.nodes[0],
            end_node=self.nodes[1],
            node_complete_rule=self.node_complete_rule,
        )

        # When: Arrow 목록 조회
        arrows = service.get_arrows(self.map.id)

        # Then: Arrow 목록이 반환되어야 함
        self.assertEqual(len(arrows), 1)
        self.assertEqual(arrows[0].id, arrow.id)
        self.assertEqual(arrows[0].start_node_id, self.nodes[0].id)
        self.assertEqual(arrows[0].end_node_id, self.nodes[1].id)
        self.assertEqual(arrows[0].active_rule_id, self.node_complete_rule.id)
        self.assertEqual(arrows[0].status, 'completed')

    def test_should_return_empty_list_when_get_arrows_with_no_arrows(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # When: Arrow가 없는 상태에서 조회
        arrows = service.get_arrows(self.map.id)

        # Then: 빈 리스트가 반환되어야 함
        self.assertEqual(len(arrows), 0)

    def test_should_return_correct_arrow_status(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # Given: Arrow 생성
        arrow1 = Arrow.objects.create(
            map=self.map,
            start_node=self.nodes[0],  # completed node
            end_node=self.nodes[1],
            node_complete_rule=self.node_complete_rule,
        )
        arrow2 = Arrow.objects.create(
            map=self.map,
            start_node=self.nodes[1],  # not completed node
            end_node=self.nodes[2],
            node_complete_rule=self.node_complete_rule,
        )

        # When: Arrow 목록 조회
        arrows = service.get_arrows(self.map.id)

        # Then: Arrow 상태가 올바르게 설정되어야 함
        arrows_by_id = {arrow.id: arrow for arrow in arrows}
        self.assertEqual(arrows_by_id[arrow1.id].status, 'completed')
        self.assertEqual(arrows_by_id[arrow2.id].status, 'locked')

    def test_should_raise_exception_when_get_arrows_with_private_map(self):
        # Given: 비공개 Map 생성
        private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            created_by=self.member,
            is_private=True,
        )

        # Given: Arrow 생성
        Arrow.objects.create(
            map=private_map,
            start_node=self.nodes[0],
            end_node=self.nodes[1],
            node_complete_rule=self.node_complete_rule,
        )

        # Given: 비회원으로 서비스 초기화
        service = MapGraphService()

        # When & Then: 비공개 Map의 Arrow 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_arrows(private_map.id)

        # When: 소유자로 서비스 초기화
        service = MapGraphService(member_id=self.member.id)
        arrows = service.get_arrows(private_map.id)

        # Then: 정상적으로 Arrow가 조회되어야 함
        self.assertEqual(len(arrows), 1)

    def test_should_return_node_complete_rules_when_get_rules(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # When: NodeCompleteRule 목록 조회
        rules = service.get_node_complete_rules(self.map.id)

        # Then: Rule 목록이 반환되어야 함
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].id, self.node_complete_rule.id)
        self.assertEqual(rules[0].name, self.node_complete_rule.name)
        self.assertEqual(rules[0].target_nodes, [self.nodes[0].id])

    def test_should_return_empty_list_when_get_rules_with_no_rules(self):
        # Given: Rule이 없는 Map 생성
        empty_map = Map.objects.create(
            name='Empty Map',
            description='Empty Description',
            created_by=self.member,
            is_private=False,
        )
        service = MapGraphService(member_id=self.member.id)

        # When: Rule 목록 조회
        rules = service.get_node_complete_rules(empty_map.id)

        # Then: 빈 리스트가 반환되어야 함
        self.assertEqual(len(rules), 0)

    def test_should_return_map_meta_when_get_map_meta(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # Given: 구독 정보 생성
        subscription = MapSubscription.objects.create(
            map=self.map,
            member=self.member,
        )

        # When: Map 메타 정보 조회
        meta = service.get_map_meta(self.map.id)

        # Then: 기본 정보 검증
        self.assertEqual(meta.id, self.map.id)
        self.assertEqual(meta.title, self.map.name)
        self.assertEqual(meta.description, self.map.description)
        self.assertEqual(meta.version, self.map.updated_at.strftime("%Y%m%d%H%M%S"))

        # Then: 통계 정보 검증
        self.assertEqual(meta.stats.total_nodes, 4)  # setUp에서 생성한 노드 수
        self.assertEqual(meta.stats.completed_nodes, 1)  # setUp에서 완료한 노드 수
        self.assertEqual(meta.stats.total_questions, 0)
        self.assertEqual(meta.stats.solved_questions, 0)

        # Then: 학습 기간 검증
        self.assertIsNotNone(meta.stats.learning_period)
        self.assertEqual(meta.stats.learning_period.start_date, subscription.created_at)
        self.assertEqual(meta.stats.learning_period.days, 60)

        # Then: 레이아웃 검증
        self.assertGreaterEqual(meta.layout.width, 300.0)
        self.assertGreaterEqual(meta.layout.height, 300.0)
        self.assertEqual(meta.layout.grid_size, 20)

        # Then: 테마 검증
        self.assertEqual(meta.theme.background_color, "#f8f9fa")
        self.assertEqual(meta.theme.grid_color, "#ddd")
        self.assertIn("completed", meta.theme.node)
        self.assertIn("in_progress", meta.theme.node)
        self.assertIn("locked", meta.theme.node)
        self.assertIn("completed", meta.theme.arrow)
        self.assertIn("locked", meta.theme.arrow)

    def test_should_return_map_meta_without_learning_period_when_not_subscribed(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # When: Map 메타 정보 조회
        meta = service.get_map_meta(self.map.id)

        # Then: 학습 기간이 None이어야 함
        self.assertIsNone(meta.stats.learning_period)

    def test_should_return_map_meta_with_correct_layout_dimensions(self):
        # Given: 서비스 초기화
        service = MapGraphService(member_id=self.member.id)

        # Given: 노드 위치 수정
        self.nodes[0].position_x = 4000
        self.nodes[0].position_y = 5000
        self.nodes[0].save()

        # When: Map 메타 정보 조회
        meta = service.get_map_meta(self.map.id)

        # Then: 레이아웃 크기가 노드 위치를 포함할 만큼 커야 함
        self.assertGreaterEqual(meta.layout.width, 4000.0)
        self.assertGreaterEqual(meta.layout.height, 4000.0)

    def test_should_raise_exception_when_get_map_meta_with_private_map(self):
        # Given: 비공개 Map 생성
        private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            created_by=self.member,
            is_private=True,
        )

        # Given: 비회원으로 서비스 초기화
        service = MapGraphService()

        # When & Then: 비공개 Map의 메타 정보 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_map_meta(private_map.id)

        # When: 소유자로 서비스 초기화
        service = MapGraphService(member_id=self.member.id)
        meta = service.get_map_meta(private_map.id)

        # Then: 정상적으로 조회되어야 함
        self.assertEqual(meta.id, private_map.id)
