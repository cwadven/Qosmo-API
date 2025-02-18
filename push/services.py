from typing import Optional, List, Dict, Any
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

from push.models import DeviceToken, PushHistory


class PushService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)

    def register_token(
        self,
        guest_id: int,
        token: str,
        device_type: str,
    ) -> DeviceToken:
        """
        디바이스 토큰 등록/갱신
        """
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
        
        histories = []
        for device_token in device_tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data or {},
                    token=device_token.token,
                )
                
                # Firebase로 푸시 발송
                response = messaging.send(message)
                
                # 발송 이력 저장
                history = PushHistory.objects.create(
                    guest_id=guest_id,
                    device_token=device_token,
                    title=title,
                    body=body,
                    data=data,
                    is_success=True,
                )
                histories.append(history)
                
            except messaging.ApiCallError as e:
                # 토큰이 유효하지 않은 경우
                if e.code in ['registration-token-not-registered', 'invalid-argument']:
                    self.deactivate_token(device_token.token)
                
                # 발송 실패 이력 저장
                history = PushHistory.objects.create(
                    guest_id=guest_id,
                    device_token=device_token,
                    title=title,
                    body=body,
                    data=data,
                    is_success=False,
                    error_message=str(e),
                )
                histories.append(history)
                
        return histories

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