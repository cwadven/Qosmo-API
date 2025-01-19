from unittest.mock import patch

from common.common_consts.common_status_codes import SuccessStatusCode
from django.test import TestCase
from django.urls import reverse
from map.models import Arrow, Map, Node, NodeCompleteRule, NodeCompletedHistory
from member.models import Guest, Member
from rest_framework import status
from rest_framework.test import APIClient


class ArrowGraphViewTest(TestCase):
    def setUp(self):
        # Given: 테스트 클라이언트 설정
        self.client = APIClient()

        # Given: 테스트 사용자 생성
        self.member = Member.objects.create(
            username='test_user',
            nickname='테스트 유저',
        )
        self.guest = Guest.objects.create(
            member=None,
            temp_nickname='testsdfsdf',
            ip='127.0.0.1',
            email='test@test.com',
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
        for i in range(3):
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
            node=self.nodes[1],
        )

        # Given: Arrow 생성
        self.arrow = Arrow.objects.create(
            map=self.map,
            start_node=self.nodes[0],
            end_node=self.nodes[1],
            node_complete_rule=self.node_complete_rule,
        )

        # Given: 첫 번째 Node 완료 처리
        NodeCompletedHistory.objects.create(
            map=self.map,
            node=self.nodes[0],
            member=self.member,
            node_complete_rule=self.node_complete_rule,
        )

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_arrow_graph_when_get_arrows(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 인증 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Arrow 그래프 API 호출
        response = self.client.get(
            reverse('map-graph:arrow-graph', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 데이터 검증
        arrows_data = response.data['data']['arrows']
        self.assertEqual(len(arrows_data), 1)

        # Then: Arrow 데이터 검증
        arrow_data = arrows_data[0]
        self.assertEqual(arrow_data['id'], self.arrow.id)
        self.assertEqual(arrow_data['start_node_id'], self.nodes[0].id)
        self.assertEqual(arrow_data['end_node_id'], self.nodes[1].id)
        self.assertEqual(arrow_data['active_rule_id'], self.node_complete_rule.id)
        self.assertEqual(arrow_data['status'], 'locked')

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_404_when_map_not_found(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 인증 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: 존재하지 않는 Map ID로 API 호출
        response = self.client.get(
            reverse('map-graph:arrow-graph', kwargs={'map_id': 99999}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
