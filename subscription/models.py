from django.db import models
from map.models import Map
from member.models import Member


class MapSubscription(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='map_subscriptions',
        help_text='구독한 사용자'
    )
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='subscriptions',
        help_text='구독한 Map'
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='구독 시작 시각',
        db_index=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Map 구독'
        verbose_name_plural = 'Map 구독'

    def __str__(self):
        return f'{self.member.nickname}의 {self.map.name} 구독'
