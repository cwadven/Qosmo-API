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

        # Given: 비공개 Map 생성
        self.private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            icon_image='private_icon.jpg',
            background_image='private_bg.jpg',
            subscriber_count=0,
            view_count=0,
            created_by=self.member,
            is_private=True,
        )

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_detail_when_request_with_valid_id(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: Guest 모킹
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

        # Then: 응답 데이터 검증
        data = response.data['data']
        self.assertEqual(data['id'], self.map.id)
        self.assertEqual(data['name'], self.map.name)
        self.assertEqual(data['description'], self.map.description)
        self.assertEqual(data['subscriber_count'], self.map.subscriber_count)
        self.assertEqual(data['view_count'], self.map.view_count)
        self.assertEqual(data['created_by']['id'], self.member.id)
        self.assertEqual(data['created_by']['nickname'], self.member.nickname)

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_404_when_request_with_invalid_id(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: Guest 모킹
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: 존재하지 않는 Map ID로 API 호출
        response = self.client.get(
            reverse('map:map-detail', kwargs={'map_id': 99999}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
        self.assertEqual(response.data['message'], '정상적인 Map 요청이 아닙니다.')

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_404_when_request_private_map_by_other_user(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 다른 사용자의 Guest 모킹
        other_member = Member.objects.create(
            username='other_user',
            nickname='다른 유저',
            member_status_id=1,
        )
        other_guest = Guest.objects.create(
            member=other_member,
            temp_nickname='other',
            ip='127.0.0.2',
            email='other@test.com',
        )
        mock_auth_cred.return_value = other_guest
        mock_jwt_decode.return_value = {'guest_id': other_guest.id, 'member_id': other_member.id}

        # When: 다른 사용자의 비공개 Map 조회 시도
        response = self.client.get(
            reverse('map:map-detail', kwargs={'map_id': self.private_map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 404 응답 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status_code'], 'map-not-found')
        self.assertEqual(response.data['message'], '정상적인 Map 요청이 아닙니다.')

    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_private_map_when_request_by_owner(
            self,
            mock_jwt_decode,
            mock_auth_cred,
    ):
        # Given: 소유자의 Guest 모킹
        self.guest.member = self.member
        self.guest.save()
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id, 'member_id': self.member.id}

        # When: 소유자가 자신의 비공개 Map 조회
        response = self.client.get(
            reverse('map:map-detail', kwargs={'map_id': self.private_map.id}),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 정상 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.private_map.id)
