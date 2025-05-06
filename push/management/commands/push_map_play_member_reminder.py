from django.core.management.base import BaseCommand

from push.consts import PushChannelType
from push.models import PushMapPlayMember
from push.services import PushService


PUSH_REMIND_TITLE = "리마인드 알림"
PUSH_REMIND_BODY = "{} 의 {} 리마인드 알림 입니다."


class Command(BaseCommand):
    """
    python manage.py push_map_play_member_reminder
    """
    help = '알림을 통해 해야할 MapPlayMember 를 통한 리마인드, 리마인더.'

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
                title=PUSH_REMIND_TITLE,
                body=PUSH_REMIND_BODY.format(map_name, map_play_title),
                data={
                    "type": PushChannelType.MAP_PLAY_MEMBER_REMINDER.value,
                    "map_id": str(push_map_play_member.map_play_member.map_play.map_id),
                },
            )
