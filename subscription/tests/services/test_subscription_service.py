from django.test import TestCase
from map.models import Map
from member.models import Member
from subscription.models import MapSubscription
from subscription.services.subscription_service import MapSubscriptionService


class MapSubscriptionServiceTest(TestCase):
    def setUp(self):
        # Given: 테스트 사용자 생성
        self.member = Member.objects.create(
            username='test_user',
            nickname='테스트 유저',
        )

        # Given: 테스트 Map 생성
        self.maps = []
        for i in range(3):
            self.maps.append(
                Map.objects.create(
                    name=f'Test Map {i}',
                    description=f'Test Description {i}',
                    icon_image=f'test_icon_{i}.jpg',
                    background_image=f'test_bg_{i}.jpg',
                    created_by=self.member,
                )
            )

        # Given: 첫 번째와 세 번째 Map 구독
        MapSubscription.objects.create(
            member=self.member,
            map=self.maps[0],
        )
        MapSubscription.objects.create(
            member=self.member,
            map=self.maps[2],
        )

    def test_should_return_all_false_when_member_id_is_none(self):
        # Given: 비회원으로 서비스 초기화
        service = MapSubscriptionService()
        map_ids = [map_obj.id for map_obj in self.maps]

        # When: 구독 상태 조회
        subscription_status = service.get_subscription_status_by_map_ids(map_ids)

        # Then: 모든 Map이 미구독 상태여야 함
        self.assertEqual(len(subscription_status), 3)
        self.assertFalse(all(subscription_status.values()))

    def test_should_return_correct_status_when_member_has_subscriptions(self):
        # Given: 회원으로 서비스 초기화
        service = MapSubscriptionService(member_id=self.member.id)
        map_ids = [map_obj.id for map_obj in self.maps]

        # When: 구독 상태 조회
        subscription_status = service.get_subscription_status_by_map_ids(map_ids)

        # Then: 구독 상태가 올바르게 반환되어야 함
        self.assertEqual(subscription_status[self.maps[0].id], True)
        self.assertEqual(subscription_status[self.maps[1].id], False)
        self.assertEqual(subscription_status[self.maps[2].id], True)

    def test_should_exclude_deleted_subscriptions(self):
        # Given: 첫 번째 Map 구독 삭제
        MapSubscription.objects.filter(
            member=self.member,
            map=self.maps[0]
        ).update(is_deleted=True)

        # Given: 회원으로 서비스 초기화
        service = MapSubscriptionService(member_id=self.member.id)
        map_ids = [map_obj.id for map_obj in self.maps]

        # When: 구독 상태 조회
        subscription_status = service.get_subscription_status_by_map_ids(map_ids)

        # Then: 삭제된 구독은 False로 반환되어야 함
        self.assertEqual(subscription_status[self.maps[0].id], False)
        self.assertEqual(subscription_status[self.maps[1].id], False)
        self.assertEqual(subscription_status[self.maps[2].id], True)

    def test_should_return_zero_when_member_id_is_none(self):
        # Given: 비회원으로 서비스 초기화
        service = MapSubscriptionService()

        # When: 구독 개수 조회
        subscription_count = service.get_member_subscription_count()

        # Then: 구독 개수가 0이어야 함
        self.assertEqual(subscription_count, 0)

    def test_should_return_correct_subscription_count(self):
        # Given: 회원으로 서비스 초기화
        service = MapSubscriptionService(member_id=self.member.id)

        # When: 구독 개수 조회
        subscription_count = service.get_member_subscription_count()

        # Then: 구독 개수가 2여야 함 (setUp에서 2개의 맵을 구독)
        self.assertEqual(subscription_count, 2)

    def test_should_exclude_deleted_subscriptions_from_count(self):
        # Given: 첫 번째 Map 구독 삭제
        MapSubscription.objects.filter(
            member=self.member,
            map=self.maps[0]
        ).update(is_deleted=True)

        # Given: 회원으로 서비스 초기화
        service = MapSubscriptionService(member_id=self.member.id)

        # When: 구독 개수 조회
        subscription_count = service.get_member_subscription_count()

        # Then: 삭제된 구독을 제외한 개수(1)가 반환되어야 함
        self.assertEqual(subscription_count, 1)
