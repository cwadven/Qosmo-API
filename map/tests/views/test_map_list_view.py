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
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_map_list_when_request_without_params(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_pagination,
    ):
        # Given: 페이지네이션 모킹 및 Guest 모킹
        mock_pagination.return_value = (self.maps[:3], True, 'next_cursor')
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

        # Then: 응답 데이터 검증
        response_data = response.data['data']
        self.assertEqual(len(response_data['maps']), 3)
        self.assertTrue(response_data['has_more'])
        self.assertEqual(response_data['next_cursor'], 'next_cursor')

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_return_filtered_maps_when_request_with_search_param(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_pagination,
    ):
        # Given: 검색 결과 모킹 및 Guest 모킹
        searched_map = self.maps[0]
        mock_pagination.return_value = ([searched_map], False, None)
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id}

        # When: 검색어와 함께 API 호출
        response = self.client.get(
            reverse('map:map-list'),
            {'search': 'Test Map 0'},
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: 응답 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], SuccessStatusCode.SUCCESS.value)

        # Then: 검색 결과 검증
        response_data = response.data['data']
        self.assertEqual(len(response_data['maps']), 1)
        self.assertEqual(response_data['maps'][0]['name'], 'Test Map 0')

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    @patch('config.middlewares.authentications.DefaultAuthentication.authenticate_credentials')
    @patch('config.middlewares.authentications.jwt_decode_handler')
    def test_should_include_member_id_when_member_exists(
            self,
            mock_jwt_decode,
            mock_auth_cred,
            mock_pagination,
    ):
        # Given: 페이지네이션 모킹 및 Member ID를 가진 Guest 모킹
        self.guest.member = self.member
        self.guest.save()
        mock_pagination.return_value = (self.maps[:3], True, 'next_cursor')
        mock_auth_cred.return_value = self.guest
        mock_jwt_decode.return_value = {'guest_id': self.guest.id, 'member_id': self.guest.member_id}

        # When: 인증된 상태로 API 호출
        response = self.client.get(
            reverse('map:map-list'),
            HTTP_AUTHORIZATION='jwt some-token'
        )

        # Then: MapService가 member_id와 함께 초기화되었는지 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_pagination.assert_called_once()

    def test_should_return_map_list_with_invalid_token(self):
        # When: 잘못된 토큰으로 Map 목록 API 호출
        response = self.client.get(
            reverse('map:map-list'),
            HTTP_AUTHORIZATION='jwt invalid-token'
        )

        # Then: 응답 검증 (토큰이 잘못되어도 게스트로 접근 가능)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status_code'], 'authentication_failed')
        self.assertEqual(response.data['message'], '자격 인증데이터(authentication credentials)가 정확하지 않습니다.')
