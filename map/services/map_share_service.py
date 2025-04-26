from django.conf import settings
from django_redis import get_redis_connection
from datetime import timedelta
import uuid

from map.models import Map
from map.exceptions import MapNotFoundException

redis_client = get_redis_connection("default")


class MapShareService:
    SHARE_KEY_PREFIX = "map:share"
    SHARE_EXPIRE_SECONDS = 1800  # 30분

    def __init__(self, member_id: int = None):
        self.member_id = member_id

    @classmethod
    def _generate_share_key(cls, map_id: int) -> str:
        """공유 키 생성"""
        return str(map_id)

    @classmethod
    def _get_redis_key(cls, share_key: str) -> str:
        """Redis 키 생성"""
        return f"{cls.SHARE_KEY_PREFIX}:{share_key}"

    def create_share_link(self, map_id: int) -> str:
        """
        Map 공유 링크 생성
        
        Args:
            map_id: Map ID
            
        Returns:
            str: 공유 키
        """
        try:
            # Map 존재 여부 확인
            _map = Map.objects.get(
                id=map_id,
                is_deleted=False,
                created_by_id=self.member_id,
            )
            
            share_key = self._generate_share_key(map_id)
            redis_key = self._get_redis_key(share_key)
            
            # Redis에 저장
            redis_client.setex(
                redis_key,
                self.SHARE_EXPIRE_SECONDS,
                map_id
            )
            
            return share_key
            
        except Map.DoesNotExist:
            raise MapNotFoundException()

    @classmethod
    def validate_share_map(cls, map_id: int) -> Map:
        """
        공유 키 검증
        
        Args:
            map_id: Map ID
            
        Returns:
            Map: 공유된 Map
            
        Raises:
            MapNotFoundException: Map을 찾을 수 없거나 접근 권한이 없는 경우
        """
        try:
            map_obj = Map.objects.get(id=map_id, is_deleted=False)
            if not map_obj.is_private:
                return map_obj
            share_key = cls._generate_share_key(map_id)
            redis_key = cls._get_redis_key(share_key)
            if not redis_client.exists(redis_key):
                raise MapNotFoundException()
            return map_obj
        except (Map.DoesNotExist, ValueError):
            raise MapNotFoundException()
