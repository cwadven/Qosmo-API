from typing import Optional, List, Dict, Any, Tuple
from exponent_server_sdk import PushClient, PushMessage, PushServerError
from django.conf import settings

from push.models import DeviceToken, PushHistory


class PushService:
    def __init__(self):
        self.client = PushClient()

    def validate_token(self, token: str) -> bool:
        """
        Expo 푸시 토큰 유효성 검사
        """
        return isinstance(token, str) and token.startswith('ExponentPushToken')

    def register_token(
        self,
        guest_id: int,
        token: str,
        device_type: str,
    ) -> DeviceToken:
        """
        디바이스 토큰 등록/갱신
        """
        # Expo 토큰 유효성 검사
        if not token or not isinstance(token, str):
            raise ValueError("토큰은 문자열이어야 합니다.")

        if not self.validate_token(token):
            raise ValueError("유효하지 않은 Expo 푸시 토큰입니다. 'ExponentPushToken'으로 시작하는 토큰이어야 합니다.")

        # 디바이스 타입 검증
        if device_type not in ['ios', 'android']:
            raise ValueError("디바이스 타입은 'ios' 또는 'android'여야 합니다.")

        device_token, _ = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'guest_id': guest_id,
                'device_type': device_type,
                'is_active': True,
            }
        )
        return device_token

    def deactivate_token(self, token: str) -> None:
        """
        디바이스 토큰 비활성화
        """
        DeviceToken.objects.filter(token=token).update(is_active=False)

    def send_push(
        self,
        guest_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> List[PushHistory]:
        """
        특정 게스트의 모든 활성화된 디바이스로 푸시 발송
        """
        device_tokens = DeviceToken.objects.filter(
            guest_id=guest_id,
            is_active=True,
        )
        
        if not device_tokens.exists():
            return []
        
        histories = []
        for device_token in device_tokens:
            try:
                # 토큰 재검증
                if not self.validate_token(device_token.token):
                    self.deactivate_token(device_token.token)
                    continue

                # Expo 푸시 발송
                success, response = self.send_notification(
                    token=device_token.token,
                    title=title,
                    body=body,
                    data=data,
                )
                
                # 발송 이력 저장
                history = PushHistory.objects.create(
                    guest_id=guest_id,
                    device_token=device_token,
                    title=title,
                    body=body,
                    data=data,
                    is_success=success,
                    error_message=None if success else str(response),
                )
                histories.append(history)
                
                # 토큰이 유효하지 않은 경우 비활성화
                if not success and isinstance(response, str) and (
                    'DeviceNotRegistered' in response or
                    'InvalidCredentials' in response or
                    'MessageTooBig' in response or
                    'MessageRateExceeded' in response
                ):
                    self.deactivate_token(device_token.token)
                
            except Exception as e:
                # 기타 예외 처리
                history = PushHistory.objects.create(
                    guest_id=guest_id,
                    device_token=device_token,
                    title=title,
                    body=body,
                    data=data,
                    is_success=False,
                    error_message=f"Unexpected error: {str(e)}",
                )
                histories.append(history)
                
        return histories

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Any]:
        """Expo 푸시 알림 전송"""
        try:
            if not self.validate_token(token):
                raise ValueError('Invalid Expo push token')

            response = self.client.publish(
                PushMessage(
                    to=token,
                    title=title,
                    body=body,
                    data=data or {}
                )
            )
            return True, response
        except PushServerError as e:
            print(f"Push server error: {e}")
            return False, str(e)
        except Exception as e:
            print(f"Push notification error: {e}")
            return False, str(e)

    def send_push_to_multiple(
        self,
        guest_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> List[PushHistory]:
        """
        여러 게스트에게 동시에 푸시 발송
        """
        all_histories = []
        for guest_id in guest_ids:
            histories = self.send_push(guest_id, title, body, data)
            all_histories.extend(histories)
        return all_histories 