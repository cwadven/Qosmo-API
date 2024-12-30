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


class MapDetailViewTest(TestCase):
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

        # Given: 테스트 Map 생성
        self.map = Map.objects.create(
            name='Test Map',
            description='Test Description',
            icon_image='test_icon.jpg',
            background_image='test_bg.jpg',
            subscriber_count=100,
            view_count=1000,
            created_by=self.member,
            is_private=False,
        )

    @patch('subscription.services.subscription_service.MapSubscriptionService.get_subscription_status_by_map_ids')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_detail_with_subscription_status(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_subscription,
    ):
        # Given: 구독 상태 모킹
        mock_subscription.return_value = {self.map.id: True}
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Map 상세 조회 API 호출
        response = self.client.get(
            reverse('map:map-detail', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 구독 상태 검증
        self.assertEqual(response.data['data']['is_subscribed'], True)

    @patch('subscription.services.subscription_service.MapSubscriptionService.get_subscription_status_by_map_ids')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_detail_with_non_subscription_status(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_subscription,
    ):
        # Given: 비구독 상태 모킹
        mock_subscription.return_value = {self.map.id: False}
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: Map 상세 조회 API 호출
        response = self.client.get(
            reverse('map:map-detail', kwargs={'map_id': self.map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 비구독 상태 검증
        self.assertEqual(response.data['data']['is_subscribed'], False)
