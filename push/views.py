from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common.common_consts.common_status_codes import SuccessStatusCode
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsGuestExists
from push.services import PushService


class DeviceTokenView(APIView):
    permission_classes = [IsGuestExists]

    def post(self, request):
        """디바이스 토큰 등록/갱신"""
        token = request.data.get('token')
        device_type = request.data.get('device_type')

        if not token or not device_type:
            return Response(
                {'error': '토큰과 디바이스 타입은 필수입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if device_type not in ['ios', 'android']:
            return Response(
                {'error': '디바이스 타입은 ios 또는 android만 가능합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = PushService()
        device_token = service.register_token(
            guest_id=request.guest.id,
            token=token,
            device_type=device_type,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'token': device_token.token,
                    'device_type': device_token.device_type,
                    'created_at': device_token.created_at,
                },
            ).model_dump(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        """디바이스 토큰 비활성화"""
        token = request.data.get('token')

        if not token:
            return Response(
                {'error': '토큰은 필수입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = PushService()
        service.deactivate_token(token)

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={},
            ).model_dump(),
            status=status.HTTP_200_OK,
        )
