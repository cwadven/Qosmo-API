from django.db import models
from .map import Map
from .node import Node


class NodeCompleteRule(models.Model):
    map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, related_name='complete_rules')
    name = models.CharField(max_length=255, help_text='해금 규칙 이름')
    node = models.ForeignKey(
        Node,
        on_delete=models.DO_NOTHING,
        related_name='complete_rules',
        help_text='타겟 Node ID'
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Node 해금 규칙'
        verbose_name_plural = 'Node 해금 규칙'

    def __str__(self):
        return f"{self.map.name} - {self.name}"
