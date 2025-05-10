from django.db import models
from member.models import (
    Guest,
    Member,
)
from push.consts import PushMapPlayMemberPushType


class DeviceToken(models.Model):
    guest = models.ForeignKey(
        Guest,
        on_delete=models.DO_NOTHING,
        related_name='device_tokens',
        help_text='토큰 소유자',
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        help_text='디바이스 토큰',
    )
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
        ],
        help_text='디바이스 타입',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='활성화 여부',
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
        verbose_name = '디바이스 토큰'
        verbose_name_plural = '디바이스 토큰'

    def __str__(self):
        return f'{self.guest.id}의 {self.device_type} 토큰'


class PushHistory(models.Model):
    guest = models.ForeignKey(
        Guest,
        on_delete=models.DO_NOTHING,
        related_name='push_histories',
        help_text='수신자',
    )
    device_token = models.ForeignKey(
        DeviceToken,
        on_delete=models.DO_NOTHING,
        related_name='push_histories',
        help_text='수신 디바이스',
    )
    title = models.CharField(
        max_length=255,
        help_text='알림 제목',
    )
    body = models.TextField(
        help_text='알림 내용',
    )
    data = models.JSONField(
        null=True,
        blank=True,
        help_text='추가 데이터',
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text='발송일시',
    )
    is_success = models.BooleanField(
        default=False,
        help_text='발송 성공 여부',
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text='실패 사유',
    )

    class Meta:
        verbose_name = '푸시 발송 이력'
        verbose_name_plural = '푸시 발송 이력'

    def __str__(self):
        return f'{self.guest.id}에게 발송된 푸시: {self.title}'


class PushMapPlayMember(models.Model):
    map_play_member = models.ForeignKey(
        'play.MapPlayMember',
        on_delete=models.DO_NOTHING,
        related_name='push_map_play_members',
        help_text='맵 플레이 멤버',
    )
    push_date = models.DateField(
        help_text='푸시 발송일',
        null=True,
        blank=True,
    )
    push_time = models.TimeField(
        help_text='푸시 발송시간',
        null=True,
        blank=True,
    )
    # Query 성능 개선을 위해서 MapPlayMember 안에는 Member 가 있지 Guest 가 있는 게 아님.
    guest = models.ForeignKey(
        Guest,
        on_delete=models.DO_NOTHING,
        help_text='푸시 수신자',
    )
    push_type = models.CharField(
        max_length=20,
        choices=PushMapPlayMemberPushType.choices(),
        help_text='푸시 타입',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='활성화 여부',
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
        verbose_name = '푸시 맵 플레이 멤버'
        verbose_name_plural = '푸시 맵 플레이 멤버'

    def __str__(self):
        return f'{self.map_play_member.member.nickname}의 푸시 맵 {self.map_play_member.map_play.map.name} 플레이 멤버'
