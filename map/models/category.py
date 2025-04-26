from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, help_text='카테고리 이름')
    description = models.TextField(help_text='카테고리 설명')
    icon = models.CharField(max_length=2048, help_text='카테고리 아이콘')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'

    def __str__(self):
        return self.name


class MapCategory(models.Model):
    map = models.ForeignKey(
        'map.Map',
        on_delete=models.DO_NOTHING,
        related_name='map_categories',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='map_categories',
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '맵 카테고리'
        verbose_name_plural = '맵 카테고리'

    def __str__(self):
        return f'{self.map.name} - {self.category.name}'
