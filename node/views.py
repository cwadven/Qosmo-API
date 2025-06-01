from common.common_consts.common_status_codes import SuccessStatusCode
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsGuestExists, IsMemberLogin
from node.services.node_detail_service import NodeDetailService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from node.services.node_management_service import NodeManagementService
from node.dtos.request_dtos import UpdateNodePropertiesRequestDTO
from node.dtos.response_dtos import UpdateNodePropertiesResponseDTO
from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus
from common.common_exceptions import PydanticAPIException


class NodeDetailView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, node_id: int, map_play_member_id: int = None):
        service = NodeDetailService(
            member_id=request.guest.member_id,
            map_play_member_id=map_play_member_id,
        )
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=service.get_node_detail(node_id).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class NodeDetailAdminView(APIView):
    permission_classes = [IsMemberLogin]

    def get(self, request, node_id: int):
        service = NodeDetailService(
            member_id=request.member.id,
            map_play_member_id=None,
        )
        management_service = NodeManagementService(node_id=node_id)
        management_service.validate_node_meta_editable(request.member.id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=service.get_node_detail_bypass(node_id).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
        
    def patch(self, request, node_id: int):
        """노드 속성 수정 (관리자 전용)"""
        # DTO를 통한 요청 데이터 검증
        try:
            dto = UpdateNodePropertiesRequestDTO.of(request)
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_UPDATE_NODE_PROPERTIES_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_UPDATE_NODE_PROPERTIES_INPUT_DATA_400.value,
                errors=e.errors(),
            )
        
        # 서비스 초기화
        management_service = NodeManagementService(node_id=node_id)
        management_service.validate_node_meta_editable(request.member.id)
        
        # 노드 속성 업데이트 (위치 정보 포함)
        updated_node = management_service.update_node_properties(
            name=dto.name,
            title=dto.title,
            description=dto.description,
            background_image=dto.background_image,
            is_active=dto.is_active,
            width=dto.width,
            height=dto.height,
            position_x=dto.position_x,
            position_y=dto.position_y
        )
        
        # 응답 DTO 생성
        response_dto = UpdateNodePropertiesResponseDTO.of(node=updated_node)
        
        # 응답 반환
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=response_dto.model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
