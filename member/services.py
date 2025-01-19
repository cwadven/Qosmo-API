import re

from common.models import BlackListWord
from member.models import (
    Member,
    MemberExtraLink,
    MemberInformation,
)
from subscription.services.subscription_service import MapSubscriptionService


def check_username_exists(username) -> bool:
    return Member.objects.filter(username=username).exists()


def check_nickname_exists(nickname) -> bool:
    return Member.objects.filter(nickname=nickname).exists()


def check_nickname_valid(nickname) -> bool:
    black_list_word_set = set(
        BlackListWord.objects.filter(
            black_list_section_id=1,
        ).values_list(
            'wording',
            flat=True,
        )
    )
    for word in black_list_word_set:
        if word in nickname:
            return False

    return True


def check_email_exists(email) -> bool:
    return Member.objects.filter(email=email).exists()


def check_only_alphanumeric(string) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9]+$', string))


def check_only_korean_english_alphanumeric(string) -> bool:
    return bool(re.match(r'^[ㄱ-ㅎ가-힣a-zA-Z0-9]+$', string))


def check_email_reg_exp_valid(email) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))


def get_active_member_information_qs(member_id: int):
    return MemberInformation.objects.filter(member_id=member_id, is_deleted=False)


def get_active_member_extra_link_qa(member_id: int):
    return MemberExtraLink.objects.filter(member_id=member_id, is_deleted=False)


def get_member_profile(member_id: int) -> dict:
    """회원의 프로필 정보를 조회합니다."""
    member = Member.objects.get(id=member_id)
    subscription_service = MapSubscriptionService(member_id=member_id)
    subscribed_map_count = subscription_service.get_member_subscription_count()

    return {
        "id": member.id,
        "nickname": member.nickname,
        "profile_image": member.profile_image_url,
        "subscribed_map_count": subscribed_map_count,
    }
