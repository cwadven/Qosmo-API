from common.common_consts.common_status_codes import SuccessStatusCode
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsGuestExists
from node.services.node_detail_service import NodeDetailService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


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
