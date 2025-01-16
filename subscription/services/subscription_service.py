from typing import (
    Dict,
    List,
    Optional,
)

from subscription.models import MapSubscription


class MapSubscriptionService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

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
