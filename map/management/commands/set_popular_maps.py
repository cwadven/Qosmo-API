from datetime import datetime
from typing import Dict

from django.core.management.base import BaseCommand
from django.db.models import (
    Count,
    QuerySet,
)

from map.models import (
    Map,
    PopularMap,
)
from subscription.models import MapSubscription


class Command(BaseCommand):
    help = '인기 맵 데이터를 최신화 합니다.'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, help='daily, monthly')

    def _get_popular_map_subscription_qs(self) -> QuerySet[Dict]:
        queryset = MapSubscription.objects.filter(
            is_deleted=False,
            map__is_deleted=False,
            map__is_private=False,
        )
        if self.type == 'daily':
            queryset = queryset.filter(
                updated_at__date=datetime.now().date()
            )
        elif self.type == 'monthly':
            queryset = queryset.filter(
                updated_at__month=datetime.now().month
            )
        else:
            queryset = MapSubscription.objects.none()
        queryset = queryset.values('map_id').annotate(
            subscriber_count=Count('member_id', distinct=True)
        ).order_by(
            '-subscriber_count'
        )
        return queryset

    def handle(self, *args, **options):
        self.type = options['type']
        if self.type not in ['daily', 'monthly']:
            self.stdout.write(self.style.ERROR('type은 daily 또는 monthly만 가능합니다.'))
            return

        popular_map_subscription_qs = self._get_popular_map_subscription_qs()[:10]
        map_by_map_id = {
            _map.id: _map
            for _map in Map.objects.filter(
                id__in=[
                    popular_map_subscription['map_id']
                    for popular_map_subscription in popular_map_subscription_qs
                ]
            )
        }
        PopularMap.objects.filter(
            type=self.type,
            is_deleted=False,
        ).update(
            is_deleted=True
        )
        PopularMap.objects.bulk_create([
            PopularMap(
                map=map_by_map_id[popular_map_subscription['map_id']],
                type=self.type,
                subscriber_count=popular_map_subscription['subscriber_count'],
                play_count=0,
            )
            for popular_map_subscription in popular_map_subscription_qs
        ])
