from typing import (
    Dict,
    List,
    Optional,
)

from django.utils import timezone

from map.services.map_service import MapService
from subscription.models import MapSubscription


class MapSubscriptionService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

    def subscribe_map_by_map_id(self, map_id: int) -> bool:
        map_service = MapService(self.member_id)
        map_detail = map_service.get_map_detail(map_id)

        if not self.member_id:
            return False

        subscription, _ = MapSubscription.objects.get_or_create(
            member_id=self.member_id,
            map_id=map_detail.id,
            defaults={
                'is_deleted': False
            }
        )
        if subscription.is_deleted:
            subscription.is_deleted = False
            subscription.save()
        return True

    def unsubscribe_map_by_map_id(self, map_id: int) -> bool:
        if not self.member_id:
            return False

        subscriptions = MapSubscription.objects.filter(
            member_id=self.member_id,
            map_id=map_id,
            is_deleted=False
        )
        if not subscriptions:
            return False

        subscriptions.update(
            is_deleted=True,
            updated_at=timezone.now()
        )
        return True

    def get_subscription_status_by_map_ids(self, map_ids: List[int]) -> Dict[int, bool]:
        if not self.member_id:
            return {map_id: False for map_id in map_ids}

        subscriptions = MapSubscription.objects.filter(
            member_id=self.member_id,
            map_id__in=map_ids,
            is_deleted=False
        ).values_list(
            'map_id',
            flat=True,
        )
        subscription_status = {
            map_id: (map_id in subscriptions)
            for map_id in map_ids
        }
        return subscription_status

    def get_member_subscription_count(self) -> int:
        """회원이 구독한 맵의 개수를 반환합니다."""
        if not self.member_id:
            return 0

        return MapSubscription.objects.filter(
            member_id=self.member_id,
            is_deleted=False
        ).count()
