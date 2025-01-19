from unittest.mock import patch

from common.common_consts.common_status_codes import SuccessStatusCode
from django.test import TestCase
from django.urls import reverse
from map.models import (
    Map,
    Node,
    NodeCompleteRule,
    NodeCompletedHistory,
)
from member.models import Guest, Member
from rest_framework import status
from rest_framework.test import APIClient


class NodeGraphViewTest(TestCase):
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
            node=self.nodes[0],
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
    def test_should_return_node_graph_when_get_nodes(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 인증 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Node 그래프 API 호출
        response = self.client.get(
            reverse('map-graph:node-graph', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 데이터 검증
        nodes_data = response.data['data']['nodes']
        self.assertEqual(len(nodes_data), 3)

        # Then: 각 노드의 필수 필드 검증
        for node_data in nodes_data:
            self.assertIn('id', node_data)
            self.assertIn('name', node_data)
            self.assertIn('position_x', node_data)
            self.assertIn('position_y', node_data)
            self.assertIn('status', node_data)

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
            reverse('map-graph:node-graph', kwargs={'map_id': 99999}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_404_when_private_map_accessed_by_non_owner(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 비공개 Map 생성
        private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            created_by=self.member,
            is_private=True,
        )

        # Given: 다른 사용자로 인증 모킹
        other_guest = Guest.objects.create(
            member=None,
            temp_nickname='other_guest',
            ip='127.0.0.2',
            email='other@test.com',
        )
        mock_auth_cred.return_value = other_guest
        mock_jwt_decode.return_value = {'guest_id': other_guest.id}

        # When: 비공개 Map에 대한 API 호출
        response = self.client.get(
            reverse('map-graph:node-graph', kwargs={'map_id': private_map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
