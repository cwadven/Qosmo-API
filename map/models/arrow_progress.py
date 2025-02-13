from django.db import models
from member.models import Member


class ArrowProgress(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='arrow_progresses',
    )
    arrow = models.ForeignKey(
        'map.Arrow',
        on_delete=models.DO_NOTHING,
        related_name='progresses',
        help_text='진행 중인 Arrow',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='arrow_progresses',
        help_text='진행 중인 사용자',
    )
    map_play_member = models.ForeignKey(
        'play.MapPlayMember',
        on_delete=models.DO_NOTHING,
        related_name='arrow_progresses',
        help_text='맵 플레이 멤버',
        null=True,
        blank=True,
    )
    is_resolved = models.BooleanField(default=False, help_text='해결 여부')
    resolved_at = models.DateTimeField(null=True, blank=True, help_text='해결된 시각')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Arrow 진행상태'
        verbose_name_plural = 'Arrow 진행상태'

    def __str__(self):
        return f'{self.member.nickname}의 {self.arrow} 진행상태'
