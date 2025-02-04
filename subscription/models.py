from django.db import models
from map.models import Map
from member.models import Member

from subscription.consts import (
    MapSubscriptionMemberDeactivateReason,
    MapSubscriptionMemberRole,
)


class MapSubscription(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='map_subscriptions',
        help_text='생성자'
    )
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='subscriptions',
        help_text='구독한 맵',
    )
    title = models.CharField(
        max_length=255,
        help_text='구독 제목',
        null=True,
        blank=True,
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
    is_deleted = models.BooleanField(
        default=False,
        help_text='삭제 여부',
    )

    class Meta:
        verbose_name = '맵 구독'
        verbose_name_plural = '맵 구독'

    def __str__(self):
        return f'{self.map.name}의 구독: {self.title}'


class MapSubscriptionMember(models.Model):
    map_subscription = models.ForeignKey(
        MapSubscription,
        on_delete=models.DO_NOTHING,
        related_name='members',
        help_text='맵 구독',
    )
    member = models.ForeignKey(
        'member.Member',
        on_delete=models.DO_NOTHING,
        related_name='map_subscription_members',
        help_text='멤버',
    )
    role = models.CharField(
        max_length=20,
        choices=MapSubscriptionMemberRole.choices(),
        help_text='역할',
    )
    deactivated = models.BooleanField(
        default=False,
        help_text='비활성화 여부',
    )
    deactivated_reason = models.CharField(
        max_length=20,
        choices=MapSubscriptionMemberDeactivateReason.choices(),
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
        verbose_name = '맵 구독 멤버'
        verbose_name_plural = '맵 구독 멤버'

    def __str__(self):
        return f'{self.member.nickname}의 {self.map_subscription.title} 구독'


class MapSubscriptionBanned(models.Model):
    map_subscription = models.ForeignKey(
        MapSubscription,
        on_delete=models.DO_NOTHING,
        related_name='banned_members',
        help_text='맵 구독',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='map_subscription_bans',
        help_text='추방된 멤버',
    )
    banned_by = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='map_subscription_ban_histories',
        help_text='추방한 admin',
    )
    banned_reason = models.TextField(
        help_text='추방 사유',
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
        verbose_name = '맵 구독 추방'
        verbose_name_plural = '맵 구독 추방'

    def __str__(self):
        return f'{self.member.nickname}의 {self.map_subscription.title} 추방'


class MapSubscriptionMemberRoleHistory(models.Model):
    map_subscription_member = models.ForeignKey(
        MapSubscriptionMember,
        on_delete=models.DO_NOTHING,
        related_name='role_histories',
        help_text='맵 구독 멤버',
    )
    previous_role = models.CharField(
        max_length=20,
        choices=MapSubscriptionMemberRole.choices(),
        help_text='이전 역할',
    )
    new_role = models.CharField(
        max_length=20,
        choices=MapSubscriptionMemberRole.choices(),
        help_text='새로운 역할',
    )
    changed_by = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='map_subscription_member_role_change_histories',
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
        verbose_name = '맵 구독 멤버 역할 변경 이력'
        verbose_name_plural = '맵 구독 멤버 역할 변경 이력'

    def __str__(self):
        return f'{self.map_subscription_member.member.nickname}의 역할 변경: {self.previous_role} -> {self.new_role}'


class MapSubscriptionInviteCode(models.Model):
    map_subscription = models.ForeignKey(
        MapSubscription,
        on_delete=models.DO_NOTHING,
        related_name='invite_codes',
        help_text='맵 구독',
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='초대 코드',
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='created_map_subscription_invite_codes',
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
        verbose_name = '맵 구독 초대 코드'
        verbose_name_plural = '맵 구독 초대 코드'

    def __str__(self):
        return f'{self.map_subscription.title}의 초대 코드: {self.code}'
