from typing import (
    List,
    Optional,
    Tuple, Type,
)

from common.common_criteria.cursor_criteria import CursorCriteria
from common.common_paginations.cursor_pagination_helpers import get_objects_with_cursor_pagination
from django.db.models import QuerySet
from map.cursor_criteria.cursor_criteria import MapListCursorCriteria
from map.exceptions import MapNotFoundException
from map.models import Map


class MapService:
    def __init__(self, member_id: Optional[int] = None):
        self.member_id = member_id

    def get_map_list(
        self,
        cursor_criteria: Type[CursorCriteria],
        search: Optional[str] = None,
        decoded_next_cursor: dict = None,
        size: int = 20,
    ) -> Tuple[List[Map], bool, Optional[str]]:
        map_qs = self._filter_map_queryset(search)
        paginated_maps, has_more, next_cursor = get_objects_with_cursor_pagination(
            map_qs,
            cursor_criteria,
            decoded_next_cursor,
            size,
        )
        return paginated_maps, has_more, next_cursor

    def _filter_map_queryset(self, search: Optional[str] = None) -> QuerySet:
        queryset = Map.objects.select_related(
            'created_by',
        ).filter(
            is_deleted=False,
            is_private=False,
        )
        if search:
            queryset = queryset.filter(
                name__icontains=search
            )
        return queryset

    def get_map_detail(self, map_id: int) -> Map:
        try:
            map_obj = Map.objects.select_related('created_by').get(
                id=map_id,
                is_deleted=False
            )
            if map_obj.is_private and map_obj.created_by_id != self.member_id:
                raise Map.DoesNotExist()
            return map_obj
        except Map.DoesNotExist:
            raise MapNotFoundException()
