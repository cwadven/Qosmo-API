from django.db import models

from map.consts import PopularMapType
from member.models import Member


class Map(models.Model):
    name = models.CharField(max_length=255, help_text='맵 이름')
    description = models.TextField(help_text='맵 설명')
    icon_image = models.CharField(max_length=2048, help_text='아이콘 이미지')
    background_image = models.CharField(max_length=2048, help_text='배경 이미지')
    subscriber_count = models.BigIntegerField(default=0, help_text='구독자 수', db_index=True)
    play_count = models.BigIntegerField(default=0, help_text='플레이 횟수', db_index=True)
    created_by = models.ForeignKey(
        Member,
        on_delete=models.DO_NOTHING,
        related_name='created_maps',
        help_text='생성자',
    )
    categories = models.ManyToManyField(
        'map.Category',
        through='map.MapCategory',
        related_name='maps',
        help_text='맵 카테고리',
    )
    is_private = models.BooleanField(default=False, help_text='비공개 여부')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '맵'
        verbose_name_plural = '맵'

    def __str__(self):
        return self.name


class PopularMap(models.Model):
    map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, related_name='popular_maps')
    type = models.CharField(
        max_length=255,
        help_text='인기 맵 타입',
        choices=PopularMapType.choices(),
    )
    subscriber_count = models.BigIntegerField(
        default=0,
        help_text='데이터 생성 시 구독자 수',
        db_index=True,
    )
    play_count = models.BigIntegerField(
        default=0,
        help_text='데이터 생성 시 플레이 횟수',
        db_index=True,
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '인기 맵'
        verbose_name_plural = '인기 맵'
