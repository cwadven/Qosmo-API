from common.common_consts.common_status_codes import (
    SuccessStatusCode,
)
from common.common_decorators.request_decorators import cursor_pagination
from common.dtos.response_dtos import BaseFormatResponse
from map.cursor_criteria.cursor_criteria import MapListCursorCriteria
from map.dtos.request_dtos import MapListRequestDTO
from map.dtos.response_dtos import (
    MapDetailDTO,
    MapListItemDTO,
    MapListResponseDTO,
)
from map.services.map_service import MapService
from member.permissions import IsGuestExists
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subscription.services.subscription_service import MapSubscriptionService


class MapListView(APIView):
    permission_classes = [
        IsGuestExists,
    ]

    @cursor_pagination(default_size=20, cursor_criteria=[MapListCursorCriteria])
    def get(self, request, decoded_next_cursor: dict, size: int):
        map_list_request = MapListRequestDTO.of(request)
        map_service = MapService(member_id=request.guest.member_id)
        paginated_maps, has_more, next_cursor = map_service.get_map_list(
            search=map_list_request.search,
            decoded_next_cursor=decoded_next_cursor,
            size=size,
        )
        subscription_service = MapSubscriptionService(member_id=request.guest.member_id)
        subscription_status = subscription_service.get_subscription_status_by_map_ids(
            [map_obj.id for map_obj in paginated_maps]
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(
                            _map,
                            is_subscribed=subscription_status[_map.id]
                        )
                        for _map in paginated_maps
                    ],
                    next_cursor=next_cursor,
                    has_more=has_more,
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapDetailView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        map_service = MapService(member_id=request.guest.member_id)
        map_obj = map_service.get_map_detail(map_id)
        subscription_service = MapSubscriptionService(member_id=request.guest.member_id)
        subscription_status = subscription_service.get_subscription_status_by_map_ids([map_id])
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapDetailDTO.from_entity(
                    map_obj,
                    is_subscribed=subscription_status[map_id]
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
