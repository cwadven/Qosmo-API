from django.db import models
from .map import Map
from .node import Node
from .node_active_rule import NodeActiveRule


class Arrow(models.Model):
    map = models.ForeignKey(
        Map, 
        on_delete=models.CASCADE,
        related_name='arrows'
    )
    start_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='starting_arrows',
        help_text="시작 Node"
    )
    end_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='ending_arrows',
        help_text="타겟 Node"
    )
    active_rule_node = models.ForeignKey(
        NodeActiveRule,
        on_delete=models.CASCADE,
        related_name='arrows',
        help_text="타겟 ActiveRuleNode"
    )
    name = models.CharField(max_length=255)
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='arrows',
        help_text="Arrow 해결 조건을 가진 문제"
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'arrows'
        ordering = ['id']

    def __str__(self):
        return f"{self.map.name} - {self.name}"
