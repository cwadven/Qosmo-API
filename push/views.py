from pydantic import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus
from common.common_consts.common_status_codes import SuccessStatusCode
from common.common_exceptions import PydanticAPIException
from common.dtos.response_dtos import BaseFormatResponse
from member.permissions import IsGuestExists, IsMemberLogin
from play.exceptions import PlayMemberNoPermissionException
from play.services import MapPlayService
from push.dtos.request_dtos import PutPushMapPlayMemberActiveRequest
from push.exceptions import PushMapPlayMemberNotFoundException
from push.services import PushService
from push.models import PushMapPlayMember
from push.consts import PushMapPlayMemberPushType
from play.models import MapPlayMember
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


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


class TestPushView(APIView):
    def post(self, request):
        """푸시 알림 테스트"""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': '토큰은 필수입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = PushService()
        success, response = service.send_notification(
            token=token,
            title="테스트 알림",
            body="이것은 테스트 푸시 알림입니다.",
            data={"type": "test", "message": "Hello from test API!"}
        )

        if success:
            return Response(
                BaseFormatResponse(
                    status_code=SuccessStatusCode.SUCCESS.value,
                    data={
                        'message': '푸시 알림 발송 성공',
                        'response': str(response)
                    },
                ).model_dump(),
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    'error': '푸시 알림 발송 실패',
                    'detail': str(response)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PushMapPlayMemberView(APIView):
    permission_classes = [IsMemberLogin]
    
    def post(self, request, map_play_member_id):
        """맵 플레이 멤버의 푸시 알림 설정 활성화"""
        active_map_play_member = MapPlayService().get_map_play_member_by_id(map_play_member_id)
        if active_map_play_member.member_id != request.member.id:
            raise PlayMemberNoPermissionException()

        push_date = request.data.get('push_date')
        push_time = request.data.get('push_time')
        remind_info = request.data.get('remind_info')
        
        PushMapPlayMember.objects.create(
            map_play_member_id=map_play_member_id,
            guest_id=request.guest.id,
            push_type=PushMapPlayMemberPushType.REMINDER.value,
            push_date=push_date,
            push_time=push_time,
            remind_info=remind_info,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class PushMapPlayDetailView(APIView):
    permission_classes = [IsMemberLogin]
    
    def put(self, request, push_map_play_member_id):
        """푸시 맵 플레이 멤버 알림 설정 수정"""
        # 존재 여부 및 소유권 확인
        try:
            push_map_play_member = PushMapPlayMember.objects.get(
                id=push_map_play_member_id,
                guest_id=request.guest.id,
                is_deleted=False,
            )
        except PushMapPlayMember.DoesNotExist:
            raise PushMapPlayMemberNotFoundException()
        
        # 요청한 사용자가 해당 푸시 설정의 소유자인지 확인
        map_play_member = push_map_play_member.map_play_member
        if map_play_member.member_id != request.member.id:
            raise PlayMemberNoPermissionException()

        # 업데이트할 필드 설정
        push_date = request.data.get('push_date')
        push_time = request.data.get('push_time')
        remind_info = request.data.get('remind_info')
        is_active = request.data.get('is_active')
        
        update_fields = ['updated_at']
        
        if push_date is not None:
            push_map_play_member.push_date = push_date
            update_fields.append('push_date')
            
        if push_time is not None:
            push_map_play_member.push_time = push_time
            update_fields.append('push_time')
            
        if remind_info is not None:
            push_map_play_member.remind_info = remind_info
            update_fields.append('remind_info')
            
        if is_active is not None:
            push_map_play_member.is_active = is_active
            update_fields.append('is_active')
        
        push_map_play_member.save(update_fields=update_fields)
        
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'id': push_map_play_member.id,
                    'push_date': push_map_play_member.push_date,
                    'push_time': push_map_play_member.push_time,
                    'remind_info': push_map_play_member.remind_info,
                    'is_active': push_map_play_member.is_active,
                    'updated_at': push_map_play_member.updated_at
                }
            ).model_dump(),
            status=status.HTTP_200_OK,
        )
    
    def delete(self, request, push_map_play_member_id):
        """푸시 맵 플레이 멤버 알림 설정 삭제"""
        try:
            push_map_play_member = PushMapPlayMember.objects.get(
                id=push_map_play_member_id,
                guest_id=request.guest.id,
                is_deleted=False,
            )
        except PushMapPlayMember.DoesNotExist:
            raise PushMapPlayMemberNotFoundException()
        
        # 요청한 사용자가 해당 푸시 설정의 소유자인지 확인
        map_play_member = push_map_play_member.map_play_member
        if map_play_member.member_id != request.member.id:
            raise PlayMemberNoPermissionException()

        push_map_play_member.is_deleted = True
        push_map_play_member.save(update_fields=['is_deleted', 'updated_at'])
        
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class PushMapPlayMemberListView(APIView):
    permission_classes = [IsMemberLogin]
    
    def get(self, request, map_play_member_id):
        """특정 맵 플레이 멤버의 푸시 알림 설정 목록 조회"""
        # map_play_member 존재 여부 확인 및 접근 권한 체크
        active_map_play_member = MapPlayService().get_map_play_member_by_id(map_play_member_id)
        if active_map_play_member.member_id != request.member.id:
            raise PlayMemberNoPermissionException()
            
        # 해당 맵 플레이 멤버의 푸시 알림 설정 조회
        push_map_play_members = PushMapPlayMember.objects.filter(
            map_play_member_id=map_play_member_id,
            guest_id=request.guest.id,
            is_deleted=False,
        ).select_related(
            'map_play_member',
            'map_play_member__map_play',
            'map_play_member__map_play__map',
        ).order_by(
            '-push_date',
            'push_time',
            '-id',
        )
        
        result = []
        for push_member in push_map_play_members:
            result.append({
                'id': push_member.id,
                'push_date': push_member.push_date,
                'push_time': push_member.push_time,
                'remind_info': push_member.remind_info,
                'is_active': push_member.is_active,
                'created_at': push_member.created_at,
                'updated_at': push_member.updated_at
            })
            
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'push_map_play_members': result
                }
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class MemberPushMapPlayMemberListView(APIView):
    permission_classes = [IsMemberLogin]

    def get(self, request):
        """사용자의 모든 활성화된 푸시 알림 설정 목록 조회"""
        # 사용자의 모든 활성화된 푸시 알림 설정 조회
        push_map_play_members = PushMapPlayMember.objects.filter(
            map_play_member__member_id=request.member.id,
            guest_id=request.guest.id,
            is_deleted=False,
        ).select_related(
            'map_play_member',
            'map_play_member__map_play',
            'map_play_member__map_play__map',
        ).order_by(
            '-push_date',
            'push_time',
        )
        
        result = []
        for push_member in push_map_play_members:
            result.append({
                'id': push_member.id,
                'map_play_member_id': push_member.map_play_member_id,
                'map_id': push_member.map_play_member.map_play.map.id,
                'map_play_id': push_member.map_play_member.map_play.id,
                'push_date': push_member.push_date,
                'push_time': push_member.push_time,
                'remind_info': push_member.remind_info,
                'is_active': push_member.is_active,
                'map_name': push_member.map_play_member.map_play.map.name,
                'map_play_title': push_member.map_play_member.map_play.title,
                'created_at': push_member.created_at,
                'updated_at': push_member.updated_at
            })
            
        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={
                    'push_map_play_members': result
                }
            ).model_dump(),
            status=status.HTTP_200_OK,
        )


class PushMapPlayMemberActiveUpdateView(APIView):
    permission_classes = [IsMemberLogin]
    
    def put(self, request):
        """여러 푸시 맵 플레이 멤버의 활성화 상태 일괄 업데이트"""
        # 요청 바디에서 데이터 추출
        try:
            put_push_map_play_member_active_request = PutPushMapPlayMemberActiveRequest(
                is_active=request.data.get('is_active'),
                push_map_play_member_ids=request.data.get('push_map_play_member_ids', []),
            )
        except ValidationError as e:
            raise PydanticAPIException(
                status_code=400,
                error_summary=InvalidInputResponseErrorStatus.INVALID_PUT_PUSH_MAP_PLAY_MEMBER_INPUT_DATA_400.label,
                error_code=InvalidInputResponseErrorStatus.INVALID_PUT_PUSH_MAP_PLAY_MEMBER_INPUT_DATA_400.value,
                errors=e.errors(),
            )

        user_push_members = PushMapPlayMember.objects.filter(
            id__in=put_push_map_play_member_active_request.push_map_play_member_ids,
            guest_id=request.guest.id,
            map_play_member__member_id=request.member.id,
            is_deleted=False,
        )

        found_ids = set(user_push_members.values_list('id', flat=True))
        not_found_ids = set(put_push_map_play_member_active_request.push_map_play_member_ids) - found_ids
        if not_found_ids:
            raise PlayMemberNoPermissionException

        service = PushService()
        service.update_push_map_play_member_active_status(
            push_map_play_member_ids=put_push_map_play_member_active_request.push_map_play_member_ids,
            is_active=put_push_map_play_member_active_request.is_active,
        )

        return Response(
            BaseFormatResponse(
                status_code=SuccessStatusCode.SUCCESS.value,
                data={},
            ).model_dump(),
            status=status.HTTP_200_OK,
        )
