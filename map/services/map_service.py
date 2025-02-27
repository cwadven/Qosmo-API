from typing import (
    List,
    Optional,
    Tuple, Type,
)

from django_redis import get_redis_connection

from common.common_criteria.cursor_criteria import CursorCriteria
from common.common_paginations.cursor_pagination_helpers import get_objects_with_cursor_pagination
from django.db.models import (
    F,
    OuterRef,
    QuerySet,
    Subquery,
)

from map.consts import PopularMapType
from map.dtos.map_dtos import MapDTO
from map.exceptions import MapNotFoundException
from map.models import Map, PopularMap
from map.services.map_share_service import MapShareService
from subscription.models import MapSubscription
from subscription.services.subscription_service import MapSubscriptionService

redis_client = get_redis_connection("default")


class MapService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

    def get_map_list(
        self,
        cursor_criteria: Type[CursorCriteria],
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        decoded_next_cursor: dict = None,
        size: int = 20,
    ) -> Tuple[List[Map], bool, Optional[str]]:
        map_qs = self._filter_map_queryset(
            search,
            category_id,
        )
        paginated_maps, has_more, next_cursor = get_objects_with_cursor_pagination(
            map_qs,
            cursor_criteria,
            decoded_next_cursor,
            size,
        )
        return paginated_maps, has_more, next_cursor

    def get_map_subscription_list(
        self,
        cursor_criteria: Type[CursorCriteria],
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        decoded_next_cursor: dict = None,
        size: int = 20,
    ) -> Tuple[List[MapSubscription], bool, Optional[str]]:
        map_subscription_qs = self._filter_subscribed_map_queryset(
            search,
            category_id,
        )
        paginated_map_subscriptions, has_more, next_cursor = get_objects_with_cursor_pagination(
            map_subscription_qs,
            cursor_criteria,
            decoded_next_cursor,
            size,
        )
        return paginated_map_subscriptions, has_more, next_cursor

    def _filter_subscribed_map_queryset(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> QuerySet:
        if not self.member_id:
            return MapSubscription.objects.none()
        latest_updated_at_subquery = (
            MapSubscription.objects.filter(
                map_id=OuterRef('map_id'),
                member_id=self.member_id,
                is_deleted=False
            ).order_by(
                '-updated_at',
            ).values(
                'updated_at',
            )[:1]
        )
        queryset = (
            MapSubscription.objects.select_related(
                'map',
                'map__created_by',
            ).filter(
                member_id=self.member_id,
                is_deleted=False
            )
            .annotate(
                latest_updated_at=Subquery(latest_updated_at_subquery),
            )
            .filter(
                updated_at=F('latest_updated_at'),
            )
        )
        if category_id:
            queryset = queryset.filter(
                map__categories__id=category_id,
            )
        if search:
            queryset = queryset.filter(
                map__name__icontains=search
            )
        return queryset

    @staticmethod
    def _filter_map_queryset(
            search: Optional[str] = None,
            category_id: Optional[int] = None,
            with_private: Optional[bool] = False,
    ) -> QuerySet:
        queryset = Map.objects.select_related(
            'created_by',
        ).prefetch_related(
            'categories',
        ).filter(
            is_deleted=False,
        )
        if not with_private:
            queryset = queryset.filter(
                is_private=False,
            )
        if category_id:
            queryset = queryset.filter(
                categories__id=category_id,
            )
        if search:
            queryset = queryset.filter(
                name__icontains=search
            )
        return queryset.distinct()

    def get_map_detail(self, map_id: int) -> MapDTO:
        try:
            map_obj = Map.objects.select_related(
                'created_by'
            ).get(
                id=map_id,
                is_deleted=False
            )
            subscription_service = MapSubscriptionService(member_id=self.member_id)
            subscription_status = subscription_service.get_subscription_status_by_map_ids([map_id])
            is_subscribed = subscription_status[map_id]
            if not map_obj.is_private:
                return MapDTO(
                    map=map_obj,
                    is_subscribed=is_subscribed,
                )
            if map_obj.created_by_id == self.member_id:
                return MapDTO(
                    map=map_obj,
                    is_subscribed=is_subscribed,
                )
            if is_subscribed:
                return MapDTO(
                    map=map_obj,
                    is_subscribed=is_subscribed,
                )
            map_share_service = MapShareService()
            return MapDTO(
                map=map_share_service.validate_share_map(map_id),
                is_subscribed=is_subscribed,
            )
        except Map.DoesNotExist:
            raise MapNotFoundException()

    @staticmethod
    def _get_popular_map_qs(_type: str) -> QuerySet[PopularMap]:
        return PopularMap.objects.select_related(
            'map',
            'map__created_by',
        ).filter(
            is_deleted=False,
            type=_type,
        ).order_by(
            '-subscriber_count',
        )

    def get_daily_popular_maps(self) -> List[Map]:
        return [
            popular_map.map
            for popular_map in self._get_popular_map_qs(PopularMapType.DAILY.value)[:5]
        ]

    def get_monthly_popular_maps(self) -> List[Map]:
        return [
            popular_map.map
            for popular_map in self._get_popular_map_qs(PopularMapType.MONTHLY.value)[:5]
        ]

    def get_my_map_list(
            self,
            cursor_criteria: Type[CursorCriteria],
            search: Optional[str] = None,
            category_id: Optional[int] = None,
            decoded_next_cursor: dict = None,
            size: int = 20,
    ) -> Tuple[List[Map], bool, Optional[str]]:
        map_qs = self._filter_map_queryset(
            search,
            category_id,
            with_private=True,
        ).filter(
            created_by_id=self.member_id,
        )
        paginated_maps, has_more, next_cursor = get_objects_with_cursor_pagination(
            map_qs,
            cursor_criteria,
            decoded_next_cursor,
            size,
        )
        return paginated_maps, has_more, next_cursor
