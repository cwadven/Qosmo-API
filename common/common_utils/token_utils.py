from datetime import (
    datetime,
    timedelta,
)

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


def jwt_encode_handler(payload: dict) -> str:
    """
    기존 jwt_encode_handler 대응
    """
    refresh = RefreshToken()
    for key, value in payload.items():
        refresh[key] = value
    return str(refresh.access_token)


def jwt_payload_handler(guest: 'Guest') -> dict:  # noqa
    payload = {
        'guest_id': guest.pk,
        'member_id': guest.member_id,
        'exp': datetime.utcnow() + settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'),
    }
    return payload


def get_jwt_login_token(member: 'Member') -> str:  # noqa
    payload = jwt_payload_handler(member.guest)
    token = jwt_encode_handler(payload)
    return token


def get_jwt_refresh_token(guest: 'Guest') -> str:  # noqa
    """
    게스트를 위한 리프레시 토큰 생성
    """
    refresh = RefreshToken()
    refresh['guest_id'] = guest.id
    refresh['member_id'] = guest.member_id
    return str(refresh)


def get_jwt_guest_token(guest: 'Guest') -> str:  # noqa
    payload = jwt_payload_handler(guest)
    token = jwt_encode_handler(payload)
    return token
