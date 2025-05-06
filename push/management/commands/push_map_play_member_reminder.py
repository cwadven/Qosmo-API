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
from push.consts import PushChannelType
from push.models import PushMapPlayMember
from push.services import PushService
from subscription.models import MapSubscription


class Command(BaseCommand):
    """
    python manage.py push_map_play_member_reminder
    """
    help = '알림을 통해 해야할 MapPlayMember 를 통한 리마인드, 리마인더.'\

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
        push_map_play_members = PushMapPlayMember.objects.select_related(
            'map_play_member__map_play__map',
            'guest__member',
        ).filter(
            is_active=True,
        )
        for push_map_play_member in push_map_play_members:
            push_service = PushService()
            map_name = push_map_play_member.map_play_member.map_play.map.name
            map_play_title = push_map_play_member.map_play_member.map_play.title
            push_service.send_push(
                guest_id=push_map_play_member.guest_id,
                title=f"Qosmo 리마인드 알림 입니다.",
                body=f"{map_name} 의 {map_play_title} 리마인드 알림 입니다.",
                data={
                    "type": "map_play_member_reminder",
                    "map_id": str(push_map_play_member.map_play_member.map_play.map_id),
                },
            )
