from django.db import models
from member.models import Member


class Map(models.Model):
    name = models.CharField(max_length=255, help_text='맵 이름')
    description = models.TextField(help_text='맵 설명')
    icon_image = models.CharField(max_length=255, help_text='아이콘 이미지')
    background_image = models.CharField(max_length=255, help_text='배경 이미지')
    subscriber_count = models.BigIntegerField(default=0, help_text='구독자 수', db_index=True)
    view_count = models.BigIntegerField(default=0, help_text='조회수', db_index=True)
    created_by = models.ForeignKey(
        Member, 
        on_delete=models.DO_NOTHING,
        related_name='created_maps',
        help_text="작성자 ID"
    )
    is_private = models.BooleanField(default=True, help_text='나만의 Map 여부')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '맵'
        verbose_name_plural = '맵'

    def __str__(self):
        return self.name
