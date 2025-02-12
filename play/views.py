from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError

from common.common_consts.common_status_codes import SuccessStatusCode
from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsMemberLogin
from play.dtos.request_dtos import (
    CreateMapPlayRequestDTO,
    CreateInviteCodeRequestDTO,
    ChangeMemberRoleRequestDTO,
    BanMemberRequestDTO,
)
from play.dtos.response_dtos import (
    MapPlayDTO,
    MapPlayMemberDTO,
    MapPlayInviteCodeDTO,
    MapPlayListDTO,
)
from play.services import MapPlayService
from play.error_messages import PlayInvalidInputResponseErrorStatus
from play.models import MapPlayMember


class MapPlayView(APIView):
    permission_classes = [IsMemberLogin]

    def get(self, request, map_id: int):
        service = MapPlayService()
        map_play_members = service.get_my_plays_by_id(
            map_id=map_id,
            member_id=request.guest.member_id,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    "plays": [
                        MapPlayListDTO.from_member(member).model_dump()
                        for member in map_play_members
                    ]
                },
            ).model_dump(),
            status=status.HTTP_200_OK,
        )

    def post(self, request, map_id: int):
        try:
            dto = CreateMapPlayRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CREATE_MAP_PLAY_ERROR_400.label,
                error_code=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CREATE_MAP_PLAY_ERROR_400.value,
                errors=e.errors(),
            )

        service = MapPlayService()
        map_play, map_play_member = service.create_map_play(
            map_id=map_id,
            title=dto.title,
            created_by_id=request.guest.member_id,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPlayDTO.from_entity(map_play).model_dump(),
            ).model_dump(),
            status=status.HTTP_201_CREATED,
        )


class MapPlayInviteCodeView(APIView):
    permission_classes = [IsMemberLogin]

    def post(self, request, map_play_id: int):
        try:
            dto = CreateInviteCodeRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CREATE_INVITE_CODE_ERROR_400.label,
                error_code=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CREATE_INVITE_CODE_ERROR_400.value,
                errors=e.errors(),
            )

        service = MapPlayService()
        invite_code = service.create_invite_code(
            map_play_id=map_play_id,
            created_by_id=request.guest.member_id,
            max_uses=dto.max_uses,
            expired_at=dto.expired_at,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPlayInviteCodeDTO.from_entity(invite_code).model_dump(),
            ).model_dump(),
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, map_play_id: int):
        service = MapPlayService()
        invite_codes = service.get_invite_codes(
            map_play_id=map_play_id,
            member_id=request.guest.member_id,
            include_inactive=False,
            include_expired=False,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    "invite_codes": [MapPlayInviteCodeDTO.from_entity(code).model_dump() for code in invite_codes]
                },
            ).model_dump(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, map_play_id: int, code: str):
        service = MapPlayService()
        service.deactivate_invite_code(
            map_play_id=map_play_id,
            code=code,
            deactivated_by_id=request.guest.member_id,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={},
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class MapPlayJoinView(APIView):
    permission_classes = [IsMemberLogin]

    def post(self, request, code: str):
        service = MapPlayService()
        member = service.join_by_invite_code(code=code, member_id=request.guest.member_id)

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPlayMemberDTO.from_entity(member).model_dump(),
            ).model_dump(),
            status=status.HTTP_201_CREATED,
        )


class MapPlayMemberRoleView(APIView):
    permission_classes = [IsMemberLogin]

    def patch(self, request, map_play_id: int, member_id: int):
        try:
            dto = ChangeMemberRoleRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CHANGE_ROLE_ERROR_400.label,
                error_code=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_CHANGE_ROLE_ERROR_400.value,
                errors=e.errors(),
            )

        service = MapPlayService()
        member = service.change_member_role(
            map_play_id=map_play_id,
            member_id=member_id,
            new_role=dto.new_role,
            changed_by_id=request.guest.member_id,
            reason=dto.reason,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPlayMemberDTO.from_entity(member).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class MapPlayMemberBanView(APIView):
    permission_classes = [IsMemberLogin]

    def post(self, request, map_play_id: int, member_id: int):
        try:
            dto = BanMemberRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_BAN_MEMBER_ERROR_400.label,
                error_code=PlayInvalidInputResponseErrorStatus.INVALID_INPUT_BAN_MEMBER_ERROR_400.value,
                errors=e.errors(),
            )

        service = MapPlayService()
        banned = service.ban_member(
            map_play_id=map_play_id,
            member_id=member_id,
            banned_by_id=request.guest.member_id,
            banned_reason=dto.banned_reason,
            invite_code_id=dto.invite_code_id,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={"banned_at": banned.banned_at},
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class MapPlayMemberDeactivateView(APIView):
    permission_classes = [IsMemberLogin]

    def post(self, request, map_play_id: int):
        service = MapPlayService()
        member = service.deactivate_member(
            map_play_id=map_play_id,
            member_id=request.guest.member_id,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=MapPlayMemberDTO.from_entity(member).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK,
        )
