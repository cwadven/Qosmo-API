from typing import Type

from django.db import models


class Arrow(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='arrows',
    )
    start_node = models.ForeignKey(
        'map.Node',
        on_delete=models.DO_NOTHING,
        related_name='starting_arrows',
        help_text='시작 Node',
    )
    node_complete_rule = models.ForeignKey(
        'map.NodeCompleteRule',
        on_delete=models.DO_NOTHING,
        related_name='arrows',
        help_text='타겟 Node 해금 규칙',
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '화살표'
        verbose_name_plural = '화살표'

    def __str__(self):
        return f'{self.map.name} - {self.start_node.name} -> {self.node_complete_rule.node.name}'

    @property
    def end_node_id(self) -> Type[int]:
        """
        end_node_id를 반환합니다.
        """
        return self.node_complete_rule.node_id
