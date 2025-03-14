# Generated by Django 4.1.10 on 2025-03-14 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0012_alter_node_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='view_count',
        ),
        migrations.RemoveField(
            model_name='popularmap',
            name='view_count',
        ),
        migrations.AddField(
            model_name='map',
            name='play_count',
            field=models.BigIntegerField(db_index=True, default=0, help_text='플레이 횟수'),
        ),
        migrations.AddField(
            model_name='popularmap',
            name='play_count',
            field=models.BigIntegerField(db_index=True, default=0, help_text='데이터 생성 시 플레이 횟수'),
        ),
    ]
