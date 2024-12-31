from common.common_consts.common_status_codes import SuccessStatusCode
from common.dtos.response_dtos import BaseFormatResponse
from map_graph.dtos.response_dtos import NodeGraphDTO
from map_graph.services.map_graph_service import MapGraphService
from member.permissions import IsGuestExists
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class NodeGraphView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        service = MapGraphService(member_id=request.guest.member_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'nodes': [
                        NodeGraphDTO.from_graph_node(node).model_dump()
                        for node in service.get_nodes(map_id)
                    ]
                }
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class ArrowGraphView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        service = MapGraphService(member_id=request.guest.member_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'arrows': [
                        arrow.model_dump()
                        for arrow in service.get_arrows(map_id)
                    ]
                }
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class NodeCompleteRuleView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        service = MapGraphService(member_id=request.guest.member_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'node_complete_rules': [
                        rule.model_dump()
                        for rule in service.get_node_complete_rules(map_id)
                    ]
                }
            ).model_dump(),
            status=status.HTTP_200_OK
        )


class MapMetaView(APIView):
    permission_classes = [IsGuestExists]

    def get(self, request, map_id: int):
        service = MapGraphService(member_id=request.guest.member_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data=service.get_map_meta(map_id).model_dump(),
            ).model_dump(),
            status=status.HTTP_200_OK
        )
