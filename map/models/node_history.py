from django.db import models
from member.models import Member


class NodeCompletedHistory(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='맵',
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
    map_subscription = models.ForeignKey(
        'subscription.MapSubscription',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='맵 구독',
        null=True,
        blank=True,
    )
    map_subscription_member = models.ForeignKey(
        'subscription.MapSubscriptionMember',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='맵 구독 멤버',
        null=True,
        blank=True,
    )
    node_complete_rule = models.ForeignKey(
        'map.NodeCompleteRule',
        on_delete=models.DO_NOTHING,
        related_name='node_completed_histories',
        help_text='해금 규칙',
    )
    completed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='해금된 시각',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='수정일시',
    )

    class Meta:
        verbose_name = '노드 해금 이력'
        verbose_name_plural = '노드 해금 이력'

    def __str__(self):
        return f'{self.member.nickname}의 {self.node.name} 해금'
