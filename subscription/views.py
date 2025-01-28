from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription.services.subscription_service import MapSubscriptionService


class MapSubscriptionView(APIView):
    def post(self, request, map_id):
        MapSubscriptionService(member_id=request.guest.member_id).subscribe_map_by_map_id(map_id)
        return Response(
            None,
            status=status.HTTP_200_OK
        )

    def delete(self, request, map_id):
        MapSubscriptionService(member_id=request.guest.member_id).unsubscribe_map_by_map_id(map_id)
        return Response(
            None,
            status=status.HTTP_200_OK
        )
