# Generated by Django 4.1.10 on 2025-01-18 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0003_map_categories_alter_map_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='height',
            field=models.FloatField(default=100),
        ),
        migrations.AddField(
            model_name='node',
            name='width',
            field=models.FloatField(default=100),
        ),
    ]
