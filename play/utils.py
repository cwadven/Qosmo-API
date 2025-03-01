import random
import logging
from datetime import datetime

import pytz
from django.utils import timezone
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

redis_client = get_redis_connection("default")


def generate_invite_code(map_play_id: int, created_at: datetime) -> str:
    """
    초대 코드 생성
    형식: "MAP-{플레이ID}-{년월일}-{시간}-{랜덤}"
    """
    # 구독 ID를 4자리 hex로 변환 (예: 1234 -> "04D2")
    play_id_hex = f"{map_play_id:04X}"
    
    # 날짜 부분: YYMMDD 형식 (예: 240205)
    date_part = created_at.strftime("%y%m%d")
    
    # 시간 부분: HHMM 형식 (예: 1423)
    time_part = created_at.strftime("%H%M")
    
    # 4자리 랜덤 문자
    random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
    
    return f"MAP-{play_id_hex}-{date_part}-{time_part}-{random_chars}"


def get_invite_code_uses_key(code: str) -> str:
    """Redis 키 생성"""
    return f"map_play:invite_code:{code}:uses"


def get_invite_code_uses(code: str) -> int:
    """Redis에서 초대 코드 사용 횟수 조회"""
    key = get_invite_code_uses_key(code)
    value = redis_client.get(key)
    return int(value) if value is not None else 0


def increment_invite_code_uses(code: str, max_uses: int = None, expired_at: datetime = None) -> bool:
    """
    초대 코드 사용 횟수 증가 (atomic)
    
    Returns:
        bool: 사용 가능한 경우 True, 초과한 경우 False
    """
    # 무제한인 경우 Redis 사용하지 않음
    if max_uses is None:
        return True
        
    key = get_invite_code_uses_key(code)

    try:
        current_uses = redis_client.incr(key)
        
        # TTL 설정
        if expired_at:
            korea_tz = pytz.timezone('Asia/Seoul')
            expired_at_kst = expired_at.astimezone(korea_tz)
            expired_at_kst_end = timezone.make_aware(
                datetime.combine(expired_at_kst.date(), datetime.max.time()),
                korea_tz,
            )
            ttl = int((expired_at_kst_end - timezone.now()).total_seconds())
            if ttl > 0:
                redis_client.expire(key, ttl)
        
        # 사용 횟수 초과 시 롤백
        if current_uses > max_uses:
            redis_client.decr(key)
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Redis operation failed: {str(e)}")
        raise
