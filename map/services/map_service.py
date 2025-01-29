from typing import (
    List,
    Optional,
    Tuple, Type,
)

from common.common_criteria.cursor_criteria import CursorCriteria
from common.common_paginations.cursor_pagination_helpers import get_objects_with_cursor_pagination
from django.db.models import QuerySet
from map.exceptions import MapNotFoundException
from map.models import Map
from subscription.models import MapSubscription


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
            return Map.objects.none()
        queryset = MapSubscription.objects.select_related(
            'map',
        ).filter(
            member_id=self.member_id,
            is_deleted=False,
        )
        if category_id:
            queryset = queryset.filter(
                map__categories__id=category_id,
            )
        if search:
            queryset = queryset.filter(
                map__name__icontains=search
            )
        return queryset.distinct('map')

    def _filter_map_queryset(
            self,
            search: Optional[str] = None,
            category_id: Optional[int] = None,
    ) -> QuerySet:
        queryset = Map.objects.select_related(
            'created_by',
        ).prefetch_related(
            'categories',
        ).filter(
            is_deleted=False,
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

    def get_map_detail(self, map_id: int) -> Map:
        try:
            map_obj = Map.objects.select_related(
                'created_by'
            ).get(
                id=map_id,
                is_deleted=False
            )
            if map_obj.is_private and map_obj.created_by_id != self.member_id:
                raise Map.DoesNotExist()
            return map_obj
        except Map.DoesNotExist:
            raise MapNotFoundException()
