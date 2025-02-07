from datetime import datetime
from typing import Optional

from django.db import transaction
from django.utils import timezone
from django.db.models import F, Q

from map.exceptions import MapNotFoundException
from map.models import Map
from play.consts import MapPlayMemberRole, MapPlayMemberDeactivateReason
from play.models import (
    MapPlay,
    MapPlayMember,
    MapPlayInviteCode,
    MapPlayBanned,
    MapPlayMemberRoleHistory,
)
from play.utils import generate_invite_code, increment_invite_code_uses
from play.exceptions import (
    PlayAdminPermissionException,
    PlayInviteCodeNotFoundException,
    PlayMemberNotFoundException,
    PlayLastAdminException,
    PlayAdminDeactivateException,
)


class MapPlayService:
    @transaction.atomic
    def create_map_play(self, map_id: int, title: str, created_by_id: int) -> MapPlay:
        """
        플레이 생성 및 admin 멤버 추가
        """
        try:
            _map = Map.objects.get(
                id=map_id,
                is_deleted=False,
            )
            if _map.is_private and _map.created_by_id != created_by_id:
                raise Map.DoesNotExist
        except Map.DoesNotExist:
            raise MapNotFoundException()

        # 플레이 생성
        map_play = MapPlay.objects.create(
            map_id=map_id,
            title=title,
            created_by_id=created_by_id,
        )

        # 생성자를 admin으로 추가
        MapPlayMember.objects.create(
            map_play=map_play,
            member_id=created_by_id,
            role=MapPlayMemberRole.ADMIN,
        )

        return map_play

    def create_invite_code(
        self,
        map_play_id: int,
        created_by_id: int,
        max_uses: Optional[int] = None,
        expired_at: Optional[datetime] = None,
    ) -> MapPlayInviteCode:
        """
        초대 코드 생성 (admin만 가능)
        """
        # admin 권한 체크
        self._validate_admin(map_play_id, created_by_id)

        now = timezone.now()
        code = generate_invite_code(map_play_id, now)

        return MapPlayInviteCode.objects.create(
            map_play_id=map_play_id,
            code=code,
            created_by_id=created_by_id,
            max_uses=max_uses,
            expired_at=expired_at,
        )

    @transaction.atomic
    def join_by_invite_code(self, code: str, member_id: int) -> MapPlayMember:
        """
        초대 코드로 플레이 참여
        """
        # 초대 코드 검증
        invite_code = self.validate_invite_code(code)

        # banned 여부 확인
        if MapPlayBanned.objects.filter(
            map_play=invite_code.map_play,
            member_id=member_id,
            invite_code=invite_code,
        ).exists():
            raise ValueError("이 초대 코드로는 더 이상 참여할 수 없습니다.")

        # 이미 active 멤버인지 확인
        if MapPlayMember.objects.filter(
            map_play=invite_code.map_play,
            member_id=member_id,
            deactivated=False,
        ).exists():
            raise ValueError("이미 플레이 멤버입니다.")

        # 사용 횟수 증가 시도
        if not increment_invite_code_uses(code, invite_code.max_uses, invite_code.expired_at):
            raise ValueError("초대 코드 사용 횟수를 초과했습니다.")

        # 멤버 생성
        map_play_member = MapPlayMember.objects.create(
            map_play=invite_code.map_play,
            member_id=member_id,
            role=MapPlayMemberRole.PARTICIPANT,
        )

        # 초대 코드 사용 횟수 업데이트 (동시성 안전하게)
        MapPlayInviteCode.objects.filter(id=invite_code.id).update(
            current_uses=F('current_uses') + 1
        )

        return map_play_member

    def _get_active_member(self, map_play_id: int, member_id: int) -> MapPlayMember:
        """
        활성화된 멤버 조회
        """
        try:
            return MapPlayMember.objects.select_related('map_play').get(
                map_play_id=map_play_id,
                member_id=member_id,
                deactivated=False,
            )
        except MapPlayMember.DoesNotExist:
            raise PlayMemberNotFoundException()

    def _is_last_admin(self, map_play_id: int) -> bool:
        """
        마지막 admin인지 체크
        """
        active_admin_count = MapPlayMember.objects.filter(
            map_play_id=map_play_id,
            role=MapPlayMemberRole.ADMIN,
            deactivated=False,
        ).count()
        return active_admin_count <= 1

    def _validate_admin_action(self, map_play_id: int, member: MapPlayMember, action: str) -> None:
        """
        admin 관련 액션 검증
        
        Args:
            map_play_id: 맵 플레이 ID
            member: 대상 멤버
            action: 수행할 액션 (탈퇴/추방/역할변경)
        """
        if member.role == MapPlayMemberRole.ADMIN and self._is_last_admin(map_play_id):
            raise PlayLastAdminException()

    def _deactivate_member(
        self, 
        member: MapPlayMember, 
        reason: MapPlayMemberDeactivateReason
    ) -> MapPlayMember:
        """
        멤버 비활성화
        """
        member.deactivated = True
        member.deactivated_reason = reason
        member.save(update_fields=['deactivated', 'deactivated_reason', 'updated_at'])
        return member

    @transaction.atomic
    def deactivate_member(self, map_play_id: int, member_id: int) -> MapPlayMember:
        """
        멤버 자발적 탈퇴
        
        1. admin이 아닌 경우: 바로 탈퇴 가능
        2. admin인 경우:
           - 혼자만 있는 경우: 바로 탈퇴 가능
           - admin이 2명 이상인 경우: 바로 탈퇴 가능
           - 다른 멤버가 있고 admin이 혼자인 경우: admin 권한 위임 필요
        """
        map_play_member = self._get_active_member(map_play_id, member_id)

        # admin이 아닌 경우 바로 탈퇴 가능
        if map_play_member.role != MapPlayMemberRole.ADMIN:
            return self._deactivate_member(map_play_member, MapPlayMemberDeactivateReason.SELF_DEACTIVATED)

        # 전체 active 멤버 수 확인
        active_member_count = MapPlayMember.objects.filter(
            map_play_id=map_play_id,
            deactivated=False,
        ).count()

        # active admin 수 확인
        active_admin_count = MapPlayMember.objects.filter(
            map_play_id=map_play_id,
            role=MapPlayMemberRole.ADMIN,
            deactivated=False,
        ).count()

        # 혼자만 있는 경우 또는 admin이 2명 이상인 경우 바로 탈퇴 가능
        if active_member_count == 1 or active_admin_count >= 2:
            return self._deactivate_member(map_play_member, MapPlayMemberDeactivateReason.SELF_DEACTIVATED)

        # 다른 멤버가 있고 admin이 혼자인 경우
        raise PlayAdminDeactivateException()

    @transaction.atomic
    def ban_member(
        self,
        map_play_id: int,
        member_id: int,
        banned_by_id: int,
        banned_reason: str,
        invite_code_id: Optional[int] = None,
    ) -> MapPlayBanned:
        """
        멤버 추방 (admin만 가능)
        """
        # admin 권한 체크
        self._validate_admin(map_play_id, banned_by_id)

        map_play_member = self._get_active_member(map_play_id, member_id)
        self._validate_admin_action(map_play_id, map_play_member, "추방")
        
        # 멤버 비활성화
        self._deactivate_member(map_play_member, MapPlayMemberDeactivateReason.BANNED)

        # 추방 이력 생성
        return MapPlayBanned.objects.create(
            map_play_id=map_play_id,
            member_id=member_id,
            banned_by_id=banned_by_id,
            invite_code_id=invite_code_id,
            banned_reason=banned_reason,
        )

    @transaction.atomic
    def change_member_role(
        self,
        map_play_id: int,
        member_id: int,
        new_role: str,
        changed_by_id: int,
        reason: Optional[str] = None,
    ) -> MapPlayMember:
        """
        멤버 역할 변경 (admin만 가능)
        """
        # admin 권한 체크
        self._validate_admin(map_play_id, changed_by_id)

        map_play_member = self._get_active_member(map_play_id, member_id)

        # 현재 역할과 같은 경우
        if map_play_member.role == new_role:
            raise ValueError("이미 해당 역할입니다.")

        # admin -> participant 변경 시 최소 1명의 admin 유지 확인
        if map_play_member.role == MapPlayMemberRole.ADMIN and new_role == MapPlayMemberRole.PARTICIPANT:
            self._validate_admin_action(map_play_id, map_play_member, "역할 변경")

        # 역할 변경 이력 생성
        MapPlayMemberRoleHistory.objects.create(
            map_play_member=map_play_member,
            previous_role=map_play_member.role,
            new_role=new_role,
            changed_by_id=changed_by_id,
            reason=reason,
        )

        # 역할 변경
        map_play_member.role = new_role
        map_play_member.save(update_fields=['role', 'updated_at'])

        return map_play_member

    def get_invite_codes(
        self,
        map_play_id: int,
        member_id: int,
        include_inactive: bool = False,
        include_expired: bool = False,
    ) -> list[MapPlayInviteCode]:
        """
        초대 코드 목록 조회 (admin만 가능)
        
        Args:
            map_play_id: 맵 플레이 ID
            member_id: 조회하는 멤버 ID
            include_inactive: 비활성화된 코드 포함 여부
            include_expired: 만료된 코드 포함 여부
        """
        # admin 권한 체크
        self._validate_admin(map_play_id, member_id)
        
        queryset = MapPlayInviteCode.objects.filter(map_play_id=map_play_id)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        if not include_expired:
            now = timezone.now()
            queryset = queryset.filter(
                Q(expired_at__isnull=True) | Q(expired_at__gt=now)
            )
            
        return list(
            queryset.select_related('map_play', 'created_by')
            .order_by('-created_at')
        )

    def get_invite_code_status(self, code: str) -> dict:
        """
        초대 코드 상태 조회
        """
        try:
            invite_code = MapPlayInviteCode.objects.get(code=code)
        except MapPlayInviteCode.DoesNotExist:
            raise ValueError("존재하지 않는 초대 코드입니다.")

        now = timezone.now()
        is_expired = invite_code.expired_at and invite_code.expired_at < now
        is_full = (
            invite_code.max_uses is not None 
            and invite_code.current_uses >= invite_code.max_uses
        )

        return {
            "is_active": invite_code.is_active,
            "is_expired": is_expired,
            "is_full": is_full,
            "current_uses": invite_code.current_uses,
            "max_uses": invite_code.max_uses,
            "expired_at": invite_code.expired_at,
        }

    @transaction.atomic
    def deactivate_invite_code(
        self, 
        map_play_id: int, 
        code: str,
        deactivated_by_id: int,
    ) -> MapPlayInviteCode:
        """
        초대 코드 비활성화 (admin만 가능)
        """
        # admin 권한 체크
        self._validate_admin(map_play_id, deactivated_by_id)

        # 초대 코드 조회
        try:
            invite_code = MapPlayInviteCode.objects.select_related('map_play').get(
                map_play_id=map_play_id,
                code=code,
                is_active=True,
            )
        except MapPlayInviteCode.DoesNotExist:
            raise PlayInviteCodeNotFoundException()

        # 비활성화
        invite_code.is_active = False
        invite_code.save(update_fields=['is_active', 'updated_at'])

        return invite_code

    def validate_invite_code(self, code: str) -> MapPlayInviteCode:
        """
        초대 코드 유효성 검증
        """
        try:
            invite_code = MapPlayInviteCode.objects.select_related('map_play').get(
                code=code,
                is_active=True,
            )
        except MapPlayInviteCode.DoesNotExist:
            raise ValueError("유효하지 않은 초대 코드입니다.")

        # 만료 여부 확인
        if invite_code.expired_at and invite_code.expired_at < timezone.now():
            raise ValueError("초대 코드가 만료되었습니다.")

        # 사용 횟수 초과 여부 확인
        if (
            invite_code.max_uses is not None 
            and invite_code.current_uses >= invite_code.max_uses
        ):
            raise ValueError("초대 코드 사용 횟수를 초과했습니다.")

        return invite_code

    def _validate_admin(self, map_play_id: int, member_id: int) -> None:
        """
        맵 플레이의 admin 권한을 체크
        """
        is_admin = MapPlayMember.objects.filter(
            map_play_id=map_play_id,
            member_id=member_id,
            role=MapPlayMemberRole.ADMIN,
            deactivated=False,
        ).exists()
        
        if not is_admin:
            raise PlayAdminPermissionException()
