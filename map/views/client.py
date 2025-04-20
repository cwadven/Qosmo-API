from common.common_consts.common_status_codes import (
    SuccessStatusCode,
)
from common.common_decorators.request_decorators import cursor_pagination
from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from map.cursor_criteria.cursor_criteria import (
    FeedbackAnswersCursorCriteria,
    MapListCursorCriteria,
    MapSubscriptionListCursorCriteria,
    MyMapListCursorCriteria,
)
from map.dtos.request_dtos import (
    MapListRequestDTO,
    MapSubscribedListRequestDTO,
    MyMapListRequestDTO,
)
from map.dtos.response_dtos import (
    MapDetailDTO,
    MapListItemDTO,
    MapListResponseDTO,
    MapPopularListResponseDTO,
)
from map.error_messages import MapInvalidInputResponseErrorStatus
from map.services.map_service import MapService
from map.services.map_share_service import MapShareService
from member.permissions import (
    IsGuestExists,
    IsMemberLogin,
)
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from node.services.node_services import get_nodes_by_map_id
from subscription.services.subscription_service import MapSubscriptionService
from django.urls import reverse


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
        map_dto = map_service.get_map_detail(map_id)
        nodes = get_nodes_by_map_id(map_id)

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapDetailDTO.from_entity(
                    map_dto.map,
                    is_subscribed=map_dto.is_subscribed,
                    is_owner=map_dto.map.created_by_id == request.guest.member_id,
                    total_node_count=len(nodes),
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapSubscribedListView(APIView):
    permission_classes = [
        IsMemberLogin,
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
        map_service = MapService(member_id=request.guest.member_id)
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


class MapPopularDailyListView(APIView):
    permission_classes = [
        IsGuestExists,
    ]

    def get(self, request):
        daily_popular_maps = MapService(member_id=request.guest.member_id).get_daily_popular_maps()
        subscription_service = MapSubscriptionService(member_id=request.guest.member_id)
        subscription_status = subscription_service.get_subscription_status_by_map_ids(
            [map_obj.id for map_obj in daily_popular_maps]
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPopularListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(
                            _map,
                            is_subscribed=subscription_status[_map.id]
                        )
                        for _map in daily_popular_maps
                    ],
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapPopularMonthlyListView(APIView):
    permission_classes = [
        IsGuestExists,
    ]

    def get(self, request):
        monthly_popular_maps = MapService(member_id=request.guest.member_id).get_monthly_popular_maps()
        subscription_service = MapSubscriptionService(member_id=request.guest.member_id)
        subscription_status = subscription_service.get_subscription_status_by_map_ids(
            [map_obj.id for map_obj in monthly_popular_maps]
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPopularListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(
                            _map,
                            is_subscribed=subscription_status[_map.id]
                        )
                        for _map in monthly_popular_maps
                    ],
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MyMapListView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

    @cursor_pagination(default_size=20, cursor_criteria=[MyMapListCursorCriteria])
    def get(self, request, decoded_next_cursor: dict, size: int):
        try:
            my_map_list_request = MyMapListRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.label,
                error_code=MapInvalidInputResponseErrorStatus.INVALID_INPUT_MAP_LIST_PARAM_ERROR_400.value,
                errors=e.errors(),
            )
        map_service = MapService(member_id=request.guest.member_id)
        paginated_my_maps, has_more, next_cursor = map_service.get_my_map_list(
            MyMapListCursorCriteria,
            search=my_map_list_request.search,
            category_id=my_map_list_request.category_id,
            decoded_next_cursor=decoded_next_cursor,
            size=size,
        )
        subscription_service = MapSubscriptionService(member_id=request.guest.member_id)
        subscription_status = subscription_service.get_subscription_status_by_map_ids(
            [map_obj.id for map_obj in paginated_my_maps]
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(
                            _map,
                            is_subscribed=subscription_status[_map.id],
                        )
                        for _map in paginated_my_maps
                    ],
                    next_cursor=next_cursor,
                    has_more=has_more,
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapShareLinkView(APIView):
    """
    Map 공유 링크 생성 API
    """
    permission_classes = [IsMemberLogin]

    def post(self, request, map_id: int):
        map_share_service = MapShareService(member_id=request.guest.member_id)
        share_code, validity_days = map_share_service.create_map_share_link(map_id)

        absolute_share_url = request.build_absolute_uri(reverse('map:map-validate-share-link', args=[map_id])) + f'?code={share_code}'

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'share_url': absolute_share_url,
                    'share_code': share_code,
                    'validity_days': validity_days,
                },
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapShareValidateView(APIView):
    """
    Map 공유 링크 검증 API
    """
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        code = request.query_params.get('code')
        if not code:
            return Response(
                BaseFormatResponse(
                    status_code=400,
                    error_summary='Invalid code',
                    error_code='INVALID_CODE',
                    message='유효하지 않은 코드입니다.',
                ).model_dump(),
                status=status.HTTP_400_BAD_REQUEST
            )

        map_share_service = MapShareService(member_id=request.guest.member_id)
        is_valid = map_share_service.validate_map_share_link(map_id, code)

        if not is_valid:
            return Response(
                BaseFormatResponse(
                    status_code=400,
                    error_summary='Invalid code',
                    error_code='INVALID_CODE',
                    message='유효하지 않은 코드입니다.',
                ).model_dump(),
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={'is_valid': True},
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapFeedbackAnswersView(APIView):
    permission_classes = [IsMemberLogin]

    @cursor_pagination(default_size=20, cursor_criteria=[FeedbackAnswersCursorCriteria])
    def get(self, request, map_id: int, decoded_next_cursor: dict, size: int):
        map_service = MapService(member_id=request.guest.member_id)
        map_obj = map_service.get_map_entity(map_id)
        if not map_obj or map_obj.created_by_id != request.guest.member_id:
            return Response(
                BaseFormatResponse(
                    status_code=403,
                    error_summary='Not your map',
                    error_code='NOT_YOUR_MAP',
                    message='내가 만든 맵만 확인할 수 있습니다.',
                ).model_dump(),
                status=status.HTTP_403_FORBIDDEN
            )

        paginated_answers, has_more, next_cursor = map_service.get_feedback_answers(
            FeedbackAnswersCursorCriteria,
            map_id=map_id,
            decoded_next_cursor=decoded_next_cursor,
            size=size,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'answers': paginated_answers,
                    'next_cursor': next_cursor,
                    'has_more': has_more,
                },
            ).model_dump(),
            status=status.HTTP_200_OK
        ) 