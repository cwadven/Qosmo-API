from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from push.consts import PushChannelType
from push.models import PushMapPlayMember
from push.services import PushService


PUSH_REMIND_TITLE = "리마인드 알림"
PUSH_REMIND_BODY = "{} 의 {} 리마인드 알림 입니다."


class Command(BaseCommand):
    """
    python manage.py push_map_play_member_reminder

    추후 개선 방향 --> 앱 진입 시, 로그인 시 알림에 필요한 정보를 받는 API 를 호출하고, 거기에 저장 되어있는 값을 기기에 등록 후, 거기서 로직 수행.
    """
    help = '알림을 통해 해야할 MapPlayMember 를 통한 리마인드, 리마인더.'

    def handle(self, *args, **options):
        datetime_now = timezone.now()
        # time 에 시간, 분 만 나오도록 초는 무조건 00
        datetime_now = datetime_now.replace(
            hour=datetime_now.hour,
            minute=datetime_now.minute,
            second=0,
            microsecond=0,
        )
        push_map_play_members = PushMapPlayMember.objects.select_related(
            'map_play_member__map_play__map',
            'guest__member',
        ).filter(
            Q(is_active=True) &
            (Q(push_date__isnull=False) | Q(push_time__isnull=False)),
            Q(push_time=datetime_now.time())
        )
        push_service = PushService()
        for push_map_play_member in push_map_play_members:
            map_name = push_map_play_member.map_play_member.map_play.map.name
            map_play_title = push_map_play_member.map_play_member.map_play.title
            push_service.send_push(
                guest_id=push_map_play_member.guest_id,
                title=PUSH_REMIND_TITLE,
                body=PUSH_REMIND_BODY.format(map_name, map_play_title),
                data={
                    "type": PushChannelType.MAP_PLAY_MEMBER_REMINDER.value,
                    "map_id": str(push_map_play_member.map_play_member.map_play.map_id),
                },
            )
