from common.common_consts.common_status_codes import (
    ErrorStatusCode,
    SuccessStatusCode,
)
from common.common_decorators.request_decorators import cursor_pagination
from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from map.cursor_criteria.cursor_criteria import MapListCursorCriteria
from map.dtos.request_dtos import MapListRequestDTO
from map.dtos.response_dtos import (
    MapListItemDTO,
    MapListResponseDTO,
)
from map.services.map_service import MapService
from member.permissions import IsGuestExists
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


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
                error_summary=ErrorStatusCode.INVALID_INPUT_HOME_LIST_PARAM_ERROR.label,
                error_code=ErrorStatusCode.INVALID_INPUT_HOME_LIST_PARAM_ERROR.value,
                errors=e.errors(),
            )

        map_service = MapService(member_id=request.guest.member_id)
        paginated_maps, has_more, next_cursor = map_service.get_map_list(
            search=map_list_request.search,
            decoded_next_cursor=decoded_next_cursor,
            size=size,
        )
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapListResponseDTO(
                    maps=[
                        MapListItemDTO.from_entity(_map)
                        for _map in paginated_maps
                    ],
                    next_cursor=next_cursor,
                    has_more=has_more,
                ).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
