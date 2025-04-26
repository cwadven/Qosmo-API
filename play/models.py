from django.db import models

from play.consts import (
    MapPlayMemberDeactivateReason,
    MapPlayMemberRole,
)


class MapPlay(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='plays',
        help_text='맵',
    )
    title = models.CharField(
        max_length=255,
        help_text='플레이 제목',
    )
    created_by = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='created_map_plays',
        help_text='생성자',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='생성일시',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '맵 플레이'
        verbose_name_plural = '맵 플레이'

    def __str__(self):
        return f'{self.map.name}의 플레이: {self.title}'


class MapPlayMember(models.Model):
    map_play = models.ForeignKey(
        MapPlay,
        on_delete=models.DO_NOTHING,
        related_name='members',
        help_text='맵 플레이',
    )
    member = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='map_play_members',
        help_text='멤버',
    )
    role = models.CharField(
        max_length=20,
        choices=MapPlayMemberRole.choices(),
        help_text='역할',
    )
    deactivated = models.BooleanField(
        default=False,
        help_text='비활성화 여부',
    )
    deactivated_reason = models.CharField(
        max_length=20,
        choices=MapPlayMemberDeactivateReason.choices(),
        null=True,
        blank=True,
        help_text='비활성화 사유',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='생성일시',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '맵 플레이 멤버'
        verbose_name_plural = '맵 플레이 멤버'

    def __str__(self):
        return f'{self.member.nickname}의 {self.map_play.title} 플레이'


class MapPlayBanned(models.Model):
    map_play = models.ForeignKey(
        MapPlay,
        on_delete=models.DO_NOTHING,
        related_name='banned_members',
        help_text='맵 플레이',
    )
    member = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='map_play_bans',
        help_text='추방된 멤버',
    )
    banned_by = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='map_play_ban_histories',
        help_text='추방한 admin',
    )
    invite_code = models.ForeignKey(
        'MapPlayInviteCode',
        on_delete=models.DO_NOTHING,
        related_name='banned_members',
        null=True,
        blank=True,
        help_text='사용한 초대 코드',
    )
    banned_reason = models.TextField(
        help_text='추방 사유',
    )
    banned_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='추방 시각',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='생성일시',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '맵 플레이 추방'
        verbose_name_plural = '맵 플레이 추방'

    def __str__(self):
        return f'{self.member.nickname}의 {self.map_play.title} 추방'


class MapPlayMemberRoleHistory(models.Model):
    map_play_member = models.ForeignKey(
        MapPlayMember,
        on_delete=models.DO_NOTHING,
        related_name='role_histories',
        help_text='맵 플레이 멤버',
    )
    previous_role = models.CharField(
        max_length=20,
        choices=MapPlayMemberRole.choices(),
        help_text='이전 역할',
    )
    new_role = models.CharField(
        max_length=20,
        choices=MapPlayMemberRole.choices(),
        help_text='새로운 역할',
    )
    changed_by = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='map_play_member_role_change_histories',
        help_text='역할 변경한 admin',
    )
    reason = models.TextField(
        null=True,
        blank=True,
        help_text='변경 사유',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='생성일시',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '맵 플레이 멤버 역할 변경 이력'
        verbose_name_plural = '맵 플레이 멤버 역할 변경 이력'

    def __str__(self):
        return f'{self.map_play_member.member.nickname}의 역할 변경: {self.previous_role} -> {self.new_role}'


class MapPlayInviteCode(models.Model):
    map_play = models.ForeignKey(
        MapPlay,
        on_delete=models.DO_NOTHING,
        related_name='invite_codes',
        help_text='맵 플레이',
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='초대 코드',
    )
    created_by = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='created_map_play_invite_codes',
        help_text='초대 코드 생성자',
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='최대 사용 횟수 (null인 경우 무제한)',
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        help_text='현재 사용 횟수',
    )
    expired_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='만료일시',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='활성화 여부',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='생성일시',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '맵 플레이 초대 코드'
        verbose_name_plural = '맵 플레이 초대 코드'

    def __str__(self):
        return f'{self.map_play.title}의 초대 코드: {self.code}'
