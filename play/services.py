from datetime import datetime
from typing import Optional, Tuple

from django.db import transaction
from django.utils import timezone
from django.db.models import F, Q, QuerySet

from map.exceptions import MapNotFoundException
from map.models import Map, NodeCompletedHistory
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
    AlreadyPlayMemberException,
    PlayAdminPermissionException,
    PlayInviteCodeNotFoundException,
    PlayMemberNotFoundException,
    PlayLastAdminException,
    PlayAdminDeactivateException,
    PlayMaximumLimitExceededException,
    PlayMemberFromInviteBannedException,
    PlayMemberInviteCodeMaxUseException, PlayMemberInvalidInviteCodeException,
    PlayMemberAlreadyDeactivatedInviteCodeException, PlayMemberAlreadyRoleException,
)
from subscription.models import MapSubscription


class MapPlayService:
    def _get_map_play_by_map_play_member_id(self, map_play_member_id: int) -> MapPlay:
        """
        맵 플레이 조회
        """
        try:
            return MapPlayMember.objects.get(
                id=map_play_member_id,
            ).map_play
        except MapPlayMember.DoesNotExist:
            raise PlayMemberNotFoundException()

    def _validate_map_play_limit(self, map_id: int, member_id: int) -> None:
        """
        사용자가 해당 Map에 대해 최대 3개까지만 플레이에 참여할 수 있는지 검증
        """
        active_play_count = MapPlayMember.objects.filter(
            map_play__map_id=map_id,
            member_id=member_id,
            deactivated=False,
        ).count()
        
        if active_play_count >= 3:
            raise PlayMaximumLimitExceededException()

    @transaction.atomic
    def create_map_play(self, map_id: int, title: str, created_by_id: int) -> Tuple[MapPlay, MapPlayMember]:
        """
        플레이 생성 및 admin 멤버 추가
        """
        # 최대 플레이 제한 검증
        self._validate_map_play_limit(map_id, created_by_id)

        # Map 접근 권한 검증
        self.validate_map_access(map_id, created_by_id)

        # 플레이 생성
        map_play = MapPlay.objects.create(
            map_id=map_id,
            title=title,
            created_by_id=created_by_id,
        )

        # 생성자를 admin으로 추가
        map_play_member = MapPlayMember.objects.create(
            map_play=map_play,
            member_id=created_by_id,
            role=MapPlayMemberRole.ADMIN,
        )

        return map_play, map_play_member

    def create_invite_code(
        self,
        map_play_member_id: int,
        created_by_id: int,
        max_uses: Optional[int] = None,
        expired_at: Optional[datetime] = None,
    ) -> MapPlayInviteCode:
        """
        초대 코드 생성 (admin만 가능)
        """
        # admin 권한 체크
        map_play = self._get_map_play_by_map_play_member_id(map_play_member_id)

        self._validate_admin(map_play.id, created_by_id)

        now = timezone.now()
        code = generate_invite_code(map_play.id, now)

        return MapPlayInviteCode.objects.create(
            map_play_id=map_play.id,
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

        # 최대 플레이 제한 검증
        self._validate_map_play_limit(invite_code.map_play.map_id, member_id)

        # banned 여부 확인
        if MapPlayBanned.objects.filter(
            map_play=invite_code.map_play,
            member_id=member_id,
            invite_code=invite_code,
        ).exists():
            raise PlayMemberFromInviteBannedException()

        # 이미 active 멤버인지 확인
        if MapPlayMember.objects.filter(
            map_play=invite_code.map_play,
            member_id=member_id,
            deactivated=False,
        ).exists():
            raise AlreadyPlayMemberException()

        # 사용 횟수 증가 시도
        if not increment_invite_code_uses(code, invite_code.max_uses, invite_code.expired_at):
            raise PlayMemberInviteCodeMaxUseException()

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

    def _get_active_member(self, map_play_member_id: int) -> MapPlayMember:
        """
        활성화된 멤버 조회
        """
        try:
            return MapPlayMember.objects.select_related('map_play').get(
                id=map_play_member_id,
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
        member.deactivated_reason = reason.value
        member.save(update_fields=['deactivated', 'deactivated_reason', 'updated_at'])
        return member

    @transaction.atomic
    def deactivate_member(
            self,
            map_play_member_id: int,
            member_id: int,
            deactivated_reason: MapPlayMemberDeactivateReason = MapPlayMemberDeactivateReason.SELF_DEACTIVATED,
    ) -> MapPlayMember:
        """
        멤버 자발적 탈퇴
        
        1. admin이 아닌 경우: 바로 탈퇴 가능
        2. admin인 경우:
           - 혼자만 있는 경우: 바로 탈퇴 가능
           - admin이 2명 이상인 경우: 바로 탈퇴 가능
           - 다른 멤버가 있고 admin이 혼자인 경우: admin 권한 위임 필요
        """
        map_play_member = self._get_active_member(map_play_member_id)

        # 본인 확인
        if map_play_member.member_id != member_id:
            raise PlayMemberNotFoundException()

        # admin이 아닌 경우 바로 탈퇴 가능
        if map_play_member.role != MapPlayMemberRole.ADMIN:
            return self._deactivate_member(map_play_member, deactivated_reason)

        # 전체 active 멤버 수 확인
        active_member_count = MapPlayMember.objects.filter(
            map_play_id=map_play_member.map_play_id,
            deactivated=False,
        ).count()

        # active admin 수 확인
        active_admin_count = MapPlayMember.objects.filter(
            map_play_id=map_play_member.map_play_id,
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
        map_play_member_id: int,
        banned_by_id: int,
        banned_reason: str,
        invite_code_id: Optional[int] = None,
    ) -> MapPlayBanned:
        """
        멤버 추방 (admin만 가능)
        """
        map_play_member = self._get_active_member(map_play_member_id)

        # admin 권한 체크
        self._validate_admin(map_play_member.map_play_id, banned_by_id)

        # admin 관련 액션 검증
        self._validate_admin_action(map_play_member.map_play_id, map_play_member, "추방")
        
        # 멤버 비활성화
        self._deactivate_member(map_play_member, MapPlayMemberDeactivateReason.BANNED)

        # 추방 이력 생성
        return MapPlayBanned.objects.create(
            map_play_id=map_play_member.map_play_id,
            member_id=map_play_member.member_id,
            banned_by_id=banned_by_id,
            invite_code_id=invite_code_id,
            banned_reason=banned_reason,
        )

    @transaction.atomic
    def change_member_role(
        self,
        map_play_member_id: int,
        new_role: str,
        changed_by_id: int,
        reason: Optional[str] = None,
    ) -> MapPlayMember:
        """
        멤버 역할 변경 (admin만 가능)
        """
        map_play_member = self._get_active_member(map_play_member_id)

        # admin 권한 체크
        self._validate_admin(map_play_member.map_play_id, changed_by_id)

        # 현재 역할과 같은 경우
        if map_play_member.role == new_role:
            raise PlayMemberAlreadyRoleException()

        # admin -> participant 변경 시 최소 1명의 admin 유지 확인
        if map_play_member.role == MapPlayMemberRole.ADMIN and new_role == MapPlayMemberRole.PARTICIPANT:
            self._validate_admin_action(map_play_member.map_play_id, map_play_member, "역할 변경")

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
        map_play_member_id: int,
        member_id: int,
        include_inactive: bool = False,
        include_expired: bool = False,
    ) -> list[MapPlayInviteCode]:
        """
        초대 코드 목록 조회 (admin만 가능)
        
        Args:
            map_play_member_id: 조회하는 맵 플레이 멤버 ID
            member_id: 조회하는 멤버 ID
            include_inactive: 비활성화된 코드 포함 여부
            include_expired: 만료된 코드 포함 여부
        """
        # admin 권한 체크
        map_play = self._get_map_play_by_map_play_member_id(map_play_member_id)

        self._validate_admin(map_play.id, member_id)
        
        queryset = MapPlayInviteCode.objects.filter(map_play_id=map_play.id)
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
            
        if not include_expired:
            now = timezone.now()
            queryset = queryset.filter(
                Q(expired_at__isnull=True) | Q(expired_at__gte=datetime.combine(now.date(), datetime.min.time()))
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
            raise PlayInviteCodeNotFoundException()

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
        map_play_member_id: int,
        code: str,
        deactivated_by_id: int,
    ) -> MapPlayInviteCode:
        """
        초대 코드 비활성화 (admin만 가능)
        """
        # admin 권한 체크
        map_play = self._get_map_play_by_map_play_member_id(map_play_member_id)

        self._validate_admin(map_play.id, deactivated_by_id)

        # 초대 코드 조회
        try:
            invite_code = MapPlayInviteCode.objects.select_related('map_play').get(
                map_play_id=map_play.id,
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
            raise PlayMemberInvalidInviteCodeException()

        # 만료 여부 확인 expired_at max 날짜
        if invite_code.expired_at and datetime.combine(invite_code.expired_at.date(), datetime.max.time()) < datetime.now():
            raise PlayMemberAlreadyDeactivatedInviteCodeException()

        # 사용 횟수 초과 여부 확인
        if (
            invite_code.max_uses is not None 
            and invite_code.current_uses >= invite_code.max_uses
        ):
            raise PlayMemberInviteCodeMaxUseException()

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

    def get_my_plays_by_id(self, map_id: int, member_id: int) -> list[MapPlayMember]:
        """
        현재 로그인한 사용자가 참여 중인 플레이 목록을 조회합니다.
        탈퇴하지 않은(deactivated=False) 플레이만 조회됩니다.
        """
        return list(
            MapPlayMember.objects.filter(
                map_play__map_id=map_id,
                member_id=member_id,
                deactivated=False,
            ).order_by(
                '-created_at',
            )
        )

    def validate_map_access(self, map_id: int, member_id: int) -> Map:
        """
        Map 접근 권한 검증 (없으면 예외 발생)
        Returns:
            Map: 검증된 Map 객체
        """
        try:
            map_obj = Map.objects.get(id=map_id, is_deleted=False)
            
            # public map인 경우 항상 접근 가능
            if not map_obj.is_private:
                return map_obj
                
            # private map인 경우 생성자이거나 활성화된 플레이 멤버인 경우만 접근 가능
            has_access = (
                map_obj.created_by_id == member_id or
                MapPlayMember.objects.filter(
                    member_id=member_id,
                    map_play__map_id=map_id,
                    deactivated=False,
                ).exists() or
                MapSubscription.objects.filter(
                    member_id=member_id,
                    map_id=map_id,
                    is_deleted=False,
                ).exists()
            )
            if not has_access:
                raise MapNotFoundException()
                
            return map_obj
        except Map.DoesNotExist:
            raise MapNotFoundException()

    def validate_map_and_play_member_access(
        self,
        map_id: int,
        member_id: int,
        map_play_member_id: Optional[int] = None,
    ) -> Map:
        """
        Map 접근 권한과 MapPlayMember 권한을 한 번에 검증
        
        Args:
            map_id: 맵 ID
            member_id: 접근하려는 멤버 ID
            map_play_member_id: 조회하려는 맵 플레이 멤버 ID (Optional)
            
        Returns:
            Map: 검증된 Map 객체
            
        Raises:
            MapNotFoundException: Map이 존재하지 않거나 접근 권한이 없는 경우
            PlayMemberNotFoundException: map_play_member_id가 주어졌으나 해당 멤버가 존재하지 않거나 비활성화된 경우
        """
        # Map 접근 권한 검증
        map_obj = self.validate_map_access(map_id, member_id)
            
        # map_play_member_id가 주어진 경우 해당 멤버 검증
        if map_play_member_id:
            member_exists = MapPlayMember.objects.filter(
                id=map_play_member_id,
                map_play__map_id=map_id,
                deactivated=False,
            ).exists()
            if not member_exists:
                raise PlayMemberNotFoundException()
            
        return map_obj

    def get_map_play_completed_node_histories(self, map_play_id: int) -> QuerySet:
        """
        특정 맵 플레이의 완료된 노드 이력을 조회합니다.
        """
        return NodeCompletedHistory.objects.filter(
            map_play_id=map_play_id,
        ).select_related(
            'node__map',
        ).order_by(
            'completed_at',
        )

    def get_map_play_member_completed_node_histories(self, map_play_member_id: int) -> QuerySet:
        """
        특정 맵 플레이의 특정 멤버가 완료한 노드 이력을 조회합니다.
        """
        return NodeCompletedHistory.objects.filter(
            map_play_member_id=map_play_member_id,
        ).select_related(
            'node__map',
        ).order_by(
            'completed_at',
        )
