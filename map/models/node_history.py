from django.db import models
from map.models import (
    Map,
    Node,
    NodeCompleteRule,
)
from member.models import Member


class NodeCompletedHistory(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
    )
    node = models.ForeignKey(
        Node,
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
        NodeCompleteRule,
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='해금 규칙',
    )
    completed_at = models.DateTimeField(auto_now_add=True, help_text='해금된 시각', db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '노드 해금 이력'
        verbose_name_plural = '노드 해금 이력'

    def __str__(self):
        return f'{self.member.nickname}의 {self.node.name} 해금'
