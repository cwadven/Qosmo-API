from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from map.exceptions import MapNotFoundException
from map.models import Map
from map.services.map_service import MapService
from member.models import Member


class MapServiceTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            username='test_user',
            nickname='테스트 유저',
        )
        self.public_maps = []
        for i in range(5):
            self.public_maps.append(
                Map.objects.create(
                    name=f'Test Map {i}',
                    description=f'Test Description {i}',
                    icon_image=f'test_icon_{i}.jpg',
                    background_image=f'test_bg_{i}.jpg',
                    subscriber_count=i * 10,
                    view_count=i * 100,
                    created_by=self.member,
                    is_private=False,
                    created_at=timezone.now(),
                )
            )
        self.private_map = Map.objects.create(
            name='Private Map',
            description='Private Description',
            icon_image='private_icon.jpg',
            background_image='private_bg.jpg',
            created_by=self.member,
            is_private=True,
        )
        self.deleted_map = Map.objects.create(
            name='Deleted Map',
            description='Deleted Description',
            icon_image='deleted_icon.jpg',
            background_image='deleted_bg.jpg',
            created_by=self.member,
            is_deleted=True,
        )

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    def test_should_return_public_maps_when_get_map_list_without_member(self, mock_pagination):
        # Given: 비회원 상태로 서비스 초기화 및 페이지네이션 모킹
        service = MapService()
        mock_pagination.return_value = (self.public_maps[:3], True, 'next_cursor')

        # When: Map 목록을 조회
        maps, has_more, next_cursor = service.get_map_list(size=3)

        # Then: 공개된 Map만 size 만큼 조회되어야 함
        self.assertEqual(len(maps), 3)
        self.assertTrue(has_more)
        self.assertEqual(next_cursor, 'next_cursor')

        # Then: 페이지네이션 함수가 올바른 인자로 호출되어야 함
        mock_pagination.assert_called_once()
        queryset_arg = mock_pagination.call_args[0][0]
        self.assertNotIn(self.private_map.id, [m.id for m in queryset_arg])
        self.assertNotIn(self.deleted_map.id, [m.id for m in queryset_arg])

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    def test_should_return_searched_maps_when_search_keyword_provided(self, mock_pagination):
        # Given: 서비스 초기화 및 페이지네이션 모킹
        service = MapService()
        searched_map = self.public_maps[1]  # Test Map 1
        mock_pagination.return_value = ([searched_map], False, None)

        # When: 특정 검색어로 Map을 검색
        maps, has_more, next_cursor = service.get_map_list(search='Test Map 1')

        # Then: 검색어가 포함된 Map만 반환되어야 함
        self.assertEqual(len(maps), 1)
        self.assertEqual(maps[0].name, 'Test Map 1')

        # Then: 페이지네이션 함수가 올바른 검색 조건으로 호출되어야 함
        mock_pagination.assert_called_once()
        queryset_arg = mock_pagination.call_args[0][0]
        self.assertEqual(queryset_arg.count(), 1)
        self.assertEqual(queryset_arg.first().name, 'Test Map 1')

        # When: 재하지 않는 검색어로 검색
        mock_pagination.return_value = ([], False, None)
        maps, has_more, next_cursor = service.get_map_list(search='Non Existing')

        # Then: 결과가 없어야 함
        self.assertEqual(len(maps), 0)

    @patch('map.services.map_service.get_objects_with_cursor_pagination')
    def test_should_paginate_maps_when_size_provided(self, mock_pagination):
        # Given: 서비스 초기화 및 첫 페이지 모킹
        service = MapService()
        mock_pagination.return_value = (self.public_maps[:2], True, 'next_cursor')

        # When: 첫 페이지 조회
        first_maps, has_more, next_cursor = service.get_map_list(size=2)

        # Then: 첫 페이지가 정상적으로 반환되어야 함
        self.assertEqual(len(first_maps), 2)
        self.assertTrue(has_more)
        self.assertEqual(next_cursor, 'next_cursor')

        # Given: 두 번째 페이지 모킹
        mock_pagination.return_value = (self.public_maps[2:4], True, 'next_cursor_2')

        # When: 다음 페이지 조회
        second_maps, has_more, next_cursor = service.get_map_list(
            size=2,
            decoded_next_cursor={'id': 'next_cursor'}
        )

        # Then: 두 번째 페이지가 정상적으로 반환되어야 함
        self.assertEqual(len(second_maps), 2)
        self.assertTrue(has_more)
        self.assertEqual(next_cursor, 'next_cursor_2')

        # Then: 페이지네이션 함수가 커서와 함께 호출되어야 함
        mock_pagination.assert_called_with(
            mock_pagination.call_args[0][0],  # queryset
            mock_pagination.call_args[0][1],  # cursor_criteria
            {'id': 'next_cursor'},  # decoded_next_cursor
            2  # size
        )

    def test_should_filter_maps_when_using_filter_queryset(self):
        # Given: 서비스 초기화
        service = MapService()

        # When: 기본 필터링 수행
        queryset = service._filter_map_queryset()

        # Then: 공개된 Map만 필터링되어야 함
        self.assertEqual(queryset.count(), 5)

        # When: 검색어로 필터링 수행
        queryset = service._filter_map_queryset(search='Test Map 1')

        # Then: 검색어가 포함된 Map만 필터링되어야 함
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, 'Test Map 1')

    def test_should_return_map_when_get_map_detail_with_valid_id(self):
        # Given: 서비스 초기화
        service = MapService()

        # When: 공개 Map 상세 조회
        map_obj = service.get_map_detail(self.public_maps[0].id)

        # Then: 요청한 Map이 반환되어야 함
        self.assertEqual(map_obj.id, self.public_maps[0].id)
        self.assertEqual(map_obj.name, self.public_maps[0].name)

    def test_should_raise_exception_when_get_map_detail_with_invalid_id(self):
        # Given: 서비스 초기화
        service = MapService()

        # When & Then: 존재하지 않는 Map ID로 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_map_detail(99999)

    def test_should_raise_exception_when_get_map_detail_with_deleted_map(self):
        # Given: 서비스 초기화
        service = MapService()

        # When & Then: 삭제된 Map 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_map_detail(self.deleted_map.id)

    def test_should_return_private_map_when_get_map_detail_by_owner(self):
        # Given: 소유자로 서비스 초기화
        service = MapService(member_id=self.member.id)

        # When: 소유자가 비공개 Map 조회
        map_obj = service.get_map_detail(self.private_map.id)

        # Then: 비공개 Map이 정상적으로 반환되어야 함
        self.assertEqual(map_obj.id, self.private_map.id)
        self.assertTrue(map_obj.is_private)

    def test_should_raise_exception_when_get_private_map_detail_by_other_user(self):
        # Given: 다른 사용자로 서비스 초기화
        other_member = Member.objects.create(
            username='other_user',
            nickname='다른 유저',
            member_status_id=1,
        )
        service = MapService(member_id=other_member.id)

        # When & Then: 다른 사용자가 비공개 Map 조회 시 예외 발생
        with self.assertRaises(MapNotFoundException):
            service.get_map_detail(self.private_map.id)
