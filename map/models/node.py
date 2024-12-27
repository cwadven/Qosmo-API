from django.db import models
from map.models import Map


class Node(models.Model):
    map = models.ForeignKey(
        Map,
        on_delete=models.DO_NOTHING,
        related_name='nodes'
    )
    name = models.CharField(max_length=255, help_text='Map 에 보이는 Node 명칭')
    title = models.CharField(max_length=255, help_text='Node 상세 페이지의 제목')
    description = models.TextField()
    background_image = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False, help_text='관리자의 활성화 여부')
    position_x = models.FloatField(db_index=True)
    position_y = models.FloatField(db_index=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '노드'
        verbose_name_plural = '노드'

    def __str__(self):
        return f"{self.map.name} - {self.name}"
