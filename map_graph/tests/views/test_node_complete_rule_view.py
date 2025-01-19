from unittest.mock import patch

from common.common_consts.common_status_codes import SuccessStatusCode
from django.test import TestCase
from django.urls import reverse
from map.models import Map, Node, NodeCompleteRule
from member.models import Guest, Member
from rest_framework import status
from rest_framework.test import APIClient


class NodeCompleteRuleViewTest(TestCase):
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
        self.node = Node.objects.create(
            map=self.map,
            name='Test Node',
            title='Test Title',
            description='Test Description',
            position_x=100,
            position_y=100,
            is_active=True,
        )

        # Given: NodeCompleteRule 생성
        self.rule = NodeCompleteRule.objects.create(
            map=self.map,
            name='Test Rule',
            node=self.node,
        )

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_node_complete_rules_when_get_rules(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 인증 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: NodeCompleteRule API 호출
        response = self.client.get(
            reverse('map-graph:node-complete-rule', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 데이터 검증
        rules_data = response.data['data']['node_complete_rules']
        self.assertEqual(len(rules_data), 1)

        # Then: Rule 데이터 검증
        rule_data = rules_data[0]
        self.assertEqual(rule_data['id'], self.rule.id)
        self.assertEqual(rule_data['name'], self.rule.name)
        self.assertEqual(rule_data['target_nodes'], [self.node.id])

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
            reverse('map-graph:node-complete-rule', kwargs={'map_id': 99999}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
