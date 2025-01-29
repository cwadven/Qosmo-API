from common.common_consts.common_status_codes import (
    SuccessStatusCode,
)
from common.common_decorators.request_decorators import cursor_pagination
from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from map.cursor_criteria.cursor_criteria import MapListCursorCriteria, MapSubscriptionListCursorCriteria
from map.dtos.request_dtos import MapListRequestDTO, MapSubscribedListRequestDTO
from map.dtos.response_dtos import (
    MapDetailDTO,
    MapDetailProgressDTO,
    MapListItemDTO,
    MapListResponseDTO, MapDetailRecentActivatedNodeDTO,
)
from map.error_messages import MapInvalidInputResponseErrorStatus
from map.services.map_service import MapService
from member.exceptions import LoginRequiredException
from member.permissions import IsGuestExists
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from node.services.node_services import (
    get_member_completed_node_histories,
    get_nodes_by_map_id,
)
from subscription.services.subscription_service import MapSubscriptionService


class MapListView(APIView):
    permission_classes = [
        IsGuestExists,
    ]

    @cursor_pagination(default_size=20, cursor_criteria=[MapListCursorCriteria])
    def get(self, request, decoded_next_cursor: dict, size: int):
        try:
            map_list_request = MapListRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.label,
                error_code=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.value,
                errors=e.errors(),
            )
        map_service = MapService(member_id=request.guest.member_id)
        paginated_maps, has_more, next_cursor = map_service.get_map_list(
            MapListCursorCriteria,
            search=map_list_request.search,
            category_id=map_list_request.category_id,
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
        is_subscribed = subscription_status[map_id]
        nodes = get_nodes_by_map_id(map_id)
        total_node_count = len(nodes)

        # 추후에 Service Layer로 이동
        if is_subscribed:
            completed_node_histories = list(
                get_member_completed_node_histories(request.guest.member_id, map_id).order_by(
                    '-completed_at',
                )
            )
            completed_node_count = len({history.node.id for history in completed_node_histories})
            map_detail_progress = MapDetailProgressDTO(
                completed_node_count=completed_node_count,
                total_node_count=total_node_count,
                percentage=int((completed_node_count/total_node_count) * 100) if total_node_count else 0,
                recent_activated_nodes=[
                    MapDetailRecentActivatedNodeDTO(
                        id=completed_node_history.node.id,
                        name=completed_node_history.node.name,
                        activated_at=completed_node_history.completed_at,
                    )
                    for completed_node_history in completed_node_histories[:3]
                ],
            )
        else:
            map_detail_progress = MapDetailProgressDTO(
                completed_node_count=0,
                total_node_count=total_node_count,
                percentage=0,
                recent_activated_nodes=[],
            )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapDetailDTO.from_entity(
                    map_obj,
                    is_subscribed=is_subscribed,
                    progress=map_detail_progress,
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapSubscribedListView(APIView):
    permission_classes = [
        IsGuestExists,
    ]

    @cursor_pagination(default_size=20, cursor_criteria=[MapSubscriptionListCursorCriteria])
    def get(self, request, decoded_next_cursor: dict, size: int):
        try:
            map_subscribed_list_request = MapSubscribedListRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.label,
                error_code=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.value,
                errors=e.errors(),
            )
        if not request.guest.member_id:
            raise LoginRequiredException()
        map_service = MapService(member_id=1)
        paginated_map_subscriptions, has_more, next_cursor = map_service.get_map_subscription_list(
            MapSubscriptionListCursorCriteria,
            search=map_subscribed_list_request.search,
            category_id=map_subscribed_list_request.category_id,
            decoded_next_cursor=decoded_next_cursor,
            size=size,
        )
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(
                            _map_subscription.map,
                            is_subscribed=True,
                        )
                        for _map_subscription in paginated_map_subscriptions
                    ],
                    next_cursor=next_cursor,
                    has_more=has_more,
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
