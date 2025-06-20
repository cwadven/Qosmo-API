from datetime import datetime
from typing import Dict

from django.core.management.base import BaseCommand
from django.db.models import (
    Count,
    QuerySet,
)
from django.utils import timezone

from map.models import (
    Map,
    PopularMap,
)
from play.models import MapPlay
from subscription.models import MapSubscription


class Command(BaseCommand):
    """
    python manage.py set_popular_maps daily
    python manage.py set_popular_maps monthly
    """
    help = '인기 맵 데이터를 최신화 합니다.'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, help='daily, monthly')

    def _get_popular_map_subscription_qs(self) -> QuerySet[Dict]:
        now = timezone.now()
        queryset = MapSubscription.objects.filter(
            is_deleted=False,
            map__is_deleted=False,
            map__is_private=False,
        )
        if self.type == 'daily':
            queryset = queryset.filter(
                updated_at__date=now.date()
            )
        elif self.type == 'monthly':
            queryset = queryset.filter(
                updated_at__gte=now.replace(day=1),
                updated_at__lt=now.replace(day=1, month=now.month+1)
            )
        else:
            queryset = MapSubscription.objects.none()
        queryset = queryset.values('map_id').annotate(
            subscriber_count=Count('member_id', distinct=True)
        ).order_by(
            '-subscriber_count'
        )
        return queryset

    def _get_popular_map_play_qs(self) -> QuerySet[Dict]:
        now = timezone.now()
        queryset = MapPlay.objects.filter(
            map__is_deleted=False,
            map__is_private=False,
        )
        if self.type == 'daily':
            queryset = queryset.filter(
                created_at__date=now.date()
            )
        elif self.type == 'monthly':
            queryset = queryset.filter(
                created_at__gte=now.replace(day=1),
                created_at__lt=now.replace(day=1, month=now.month + 1)
            )
        else:
            queryset = MapPlay.objects.none()
        queryset = queryset.values('map_id').annotate(
            play_count=Count('created_by_id', distinct=True)
        ).order_by(
            '-play_count'
        )
        return queryset

    def handle(self, *args, **options):
        self.type = options['type']
        if self.type not in ['daily', 'monthly']:
            self.stdout.write(self.style.ERROR('type은 daily 또는 monthly만 가능합니다.'))
            return

        map_id_set = set()
        popular_map_subscription_qs = self._get_popular_map_subscription_qs()[:10]
        popular_map_subscription_mapper = {
            popular_map_subscription['map_id']: popular_map_subscription
            for popular_map_subscription in popular_map_subscription_qs
        }
        popular_map_play_qs = self._get_popular_map_play_qs()[:10]
        popular_map_play_mapper = {
            popular_map_play['map_id']: popular_map_play
            for popular_map_play in popular_map_play_qs
        }
        map_id_set.update([
            popular_map_subscription['map_id']
            for popular_map_subscription in popular_map_subscription_qs
        ])
        map_id_set.update([
            popular_map_play['map_id']
            for popular_map_play in popular_map_play_qs
        ])
        if not map_id_set:
            self.stdout.write(self.style.ERROR('인기 맵이 없습니다.'))
            return

        # Get only 10 going to be popular maps
        going_to_be_popular_map_qs = Map.objects.filter(
            is_deleted=False,
            is_private=False,
            id__in=map_id_set,
        )[:10]
        # Delete all popular maps
        PopularMap.objects.filter(
            type=self.type,
            is_deleted=False,
        ).update(
            is_deleted=True
        )
        # Create new popular maps
        PopularMap.objects.bulk_create([
            PopularMap(
                map_id=going_to_be_popular_map.id,
                type=self.type,
                subscriber_count=popular_map_subscription_mapper.get('map_id', {}).get('subscriber_count', 0),
                play_count=popular_map_play_mapper.get('map_id', {}).get('play_count', 0),
            )
            for going_to_be_popular_map in going_to_be_popular_map_qs
        ])
