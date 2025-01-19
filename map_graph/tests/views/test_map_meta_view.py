from unittest.mock import patch

from common.common_consts.common_status_codes import SuccessStatusCode
from django.test import TestCase
from django.urls import reverse
from map.models import Map, Node, NodeCompleteRule, NodeCompletedHistory
from member.models import Guest, Member
from rest_framework import status
from rest_framework.test import APIClient
from subscription.models import MapSubscription


class MapMetaViewTest(TestCase):
    def setUp(self):
        # Given: 테스트 클라이언트 설정
        self.client = APIClient()

        # Given: 테스트 사용자 생성
        self.member = Member.objects.create(
            username='test_user',
            nickname='테스트 유저',
            member_status_id=1,
        )
        self.guest = Guest.objects.create(
            member=self.member,
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

        # Given: Node 완료 처리
        NodeCompletedHistory.objects.create(
            map=self.map,
            node=self.node,
            member=self.member,
            node_complete_rule=self.rule,
        )

        # Given: 구독 정보 생성
        self.subscription = MapSubscription.objects.create(
            map=self.map,
            member=self.member,
        )

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_meta_when_get_meta(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 인증 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Map 메타 정보 API 호출
        response = self.client.get(
            reverse('map-graph:map-meta', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 데이터 검증
        meta_data = response.data['data']
        self.assertEqual(meta_data['id'], self.map.id)
        self.assertEqual(meta_data['title'], self.map.name)
        self.assertEqual(meta_data['description'], self.map.description)
        self.assertEqual(meta_data['version'], self.map.updated_at.strftime("%Y%m%d%H%M%S"))

        # Then: 통계 정보 검증
        stats = meta_data['stats']
        self.assertEqual(stats['total_nodes'], 1)
        self.assertEqual(stats['completed_nodes'], 1)
        self.assertEqual(stats['total_questions'], 0)
        self.assertEqual(stats['solved_questions'], 0)

        # Then: 레이아웃 검증
        layout = meta_data['layout']
        self.assertGreaterEqual(layout['width'], 100.0)
        self.assertGreaterEqual(layout['height'], 100.0)
        self.assertEqual(layout['grid_size'], 20)

        # Then: 테마 검증
        theme = meta_data['theme']
        self.assertEqual(theme['background_color'], "#f8f9fa")
        self.assertEqual(theme['grid_color'], "#ddd")
        self.assertIn("completed", theme['node'])
        self.assertIn("in_progress", theme['node'])
        self.assertIn("locked", theme['node'])
        self.assertIn("completed", theme['arrow'])
        self.assertIn("locked", theme['arrow'])

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
            reverse('map-graph:map-meta', kwargs={'map_id': 99999}),
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
            temp_nickname='other_user',
            ip='127.0.0.2',
            email='other@test.com',
        )
        mock_auth_cred.return_value = other_guest
        mock_jwt_decode.return_value = {'guest_id': other_guest.id}

        # When: 비공개 Map의 메타 정보 API 호출
        response = self.client.get(
            reverse('map-graph:map-meta', kwargs={'map_id': private_map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
