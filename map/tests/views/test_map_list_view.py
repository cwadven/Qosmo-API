from unittest.mock import patch

from common.common_consts.common_status_codes import SuccessStatusCode
from django.test import TestCase
from django.urls import reverse
from map.models import Map
from member.models import (
    Guest,
    Member,
)
from rest_framework import status
from rest_framework.test import APIClient


class MapListViewTest(TestCase):
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
            member=None,
            temp_nickname='testsdfsdf',
            ip='127.0.0.1',
            email='test@test.com',
        )

        # Given: 테스트 Map 데이터 생성
        self.maps = []
        for i in range(5):
            self.maps.append(
                Map.objects.create(
                    name=f'Test Map {i}',
                    description=f'Test Description {i}',
                    icon_image=f'test_icon_{i}.jpg',
                    background_image=f'test_bg_{i}.jpg',
                    subscriber_count=i * 10,
                    view_count=i * 100,
                    created_by=self.member,
                    is_private=False,
                )
            )

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    @patch('subscription.services.subscription_service.MapSubscriptionService.get_subscription_status_by_map_ids')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_list_with_subscription_status(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_subscription,
            mock_pagination,
    ):
        # Given: 페이지네이션 및 구독 상태 모킹
        mock_pagination.return_value = (self.maps[:3], True, 'next_cursor')
        mock_subscription.return_value = {
            self.maps[0].id: True,
            self.maps[1].id: False,
            self.maps[2].id: True,
        }
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Map 목록 API 호출
        response = self.client.get(
            reverse('map:map-list'),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 구독 상태 검증
        maps_data = response.data['data']['maps']
        self.assertEqual(maps_data[0]['is_subscribed'], True)
        self.assertEqual(maps_data[1]['is_subscribed'], False)
        self.assertEqual(maps_data[2]['is_subscribed'], True)

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    @patch('subscription.services.subscription_service.MapSubscriptionService.get_subscription_status_by_map_ids')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_fail_when_invalid_category_id(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_subscription,
            mock_pagination,
    ):
        # Given: 페이지네이션 및 구독 상태 모킹
        mock_pagination.return_value = (self.maps[:3], True, 'next_cursor')
        mock_subscription.return_value = {
            self.maps[0].id: True,
            self.maps[1].id: False,
            self.maps[2].id: True,
        }
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Map category_id 이상하게 목록 API 호출
        response = self.client.get(
            reverse('map:map-list'),
            {'category_id': 'invalid'},
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status_code'], 'invalid-map-list-input')
        self.assertEqual(response.data['message'], '입력값을 다시 한번 확인해주세요.')
        self.assertEqual(set(response.data['errors'].keys()), {'category_id'})
