from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.common_consts.common_status_codes import SuccessStatusCode
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsMemberLogin
from subscription.services.subscription_service import MapSubscriptionService


class MapSubscriptionView(APIView):
    permission_classes = [
        IsMemberLogin,
    ]

    def post(self, request, map_id):
        MapSubscriptionService(member_id=request.guest.member_id).subscribe_map_by_map_id(map_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={},
            ).model_dump(),
            status=status.HTTP_200_OK
        )

    def delete(self, request, map_id):
        MapSubscriptionService(member_id=request.guest.member_id).unsubscribe_map_by_map_id(map_id)
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={},
            ).model_dump(),
            status=status.HTTP_200_OK
        )
