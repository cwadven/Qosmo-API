from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from push.models import (
    DeviceToken,
    PushHistory,
)


class PushService:
    def validate_token(self, token: str) -> bool:
        """
        FCM 토큰 유효성 검사
        """
        try:
            # 테스트 메시지 생성 (실제로 발송하지는 않음)
            messaging.Message(
                notification=messaging.Notification(
                    title='Token Validation',
                    body='Validating FCM token',
                ),
                token=token,
            )
            return True
        except ValueError:
            return False

    def register_token(
        self,
        guest_id: int,
        token: str,
        device_type: str,
    ) -> DeviceToken:
        """
        디바이스 토큰 등록/갱신
        """
        # FCM 토큰 유효성 검사
        if not token or not isinstance(token, str):
            raise ValueError("토큰은 문자열이어야 합니다.")

        if not self.validate_token(token):
            raise ValueError("유효하지 않은 FCM 토큰입니다.")

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

                # 데이터에 title과 body 추가
                message_data = data or {}
                message_data.update({
                    'title': title,
                    'body': body,
                    'notification_title': title,
                    'notification_body': body,
                })

                message = messaging.Message(
                    data=message_data,  # notification 키 없이 data만 사용
                    android=messaging.AndroidConfig(
                        priority='high',
                        ttl=86400,  # 24시간
                    ),
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
                
            except FirebaseError as e:
                error_message = str(e).lower()
                # 토큰이 유효하지 않은 경우 체크
                if any(msg in error_message for msg in [
                    'not a valid fcm registration token',
                    'requested entity was not found',
                    'invalid argument',
                    'registration token not valid'
                ]):
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
        """Firebase 푸시 알림 전송"""
        try:
            if not self.validate_token(token):
                raise ValueError('Invalid FCM token')

            message = messaging.Message(
                data=data or {},
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='default',
                        priority='max',
                        default_sound=True,
                        default_vibrate_timings=True,
                        click_action='OPEN_ACTIVITY_1',
                    ),
                    data=data or {},
                ),
                token=token,
            )
            
            response = messaging.send(message)
            return True, response
        except FirebaseError as e:
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