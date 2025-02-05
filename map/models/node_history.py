from django.db import models
from member.models import Member


class NodeCompletedHistory(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
    )
    node = models.ForeignKey(
        'map.Node',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='해금된 Node',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='해금한 사용자',
    )
    node_complete_rule = models.ForeignKey(
        'map.NodeCompleteRule',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='해금 규칙',
    )
    map_play = models.ForeignKey(
        'play.MapPlay',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='맵 플레이',
        null=True,
        blank=True,
    )
    map_play_member = models.ForeignKey(
        'play.MapPlayMember',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='맵 플레이 멤버',
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(auto_now_add=True, help_text='해금된 시각', db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '노드 해금 이력'
        verbose_name_plural = '노드 해금 이력'

    def __str__(self):
        return f'{self.member.nickname}의 {self.node.name} 해금'
