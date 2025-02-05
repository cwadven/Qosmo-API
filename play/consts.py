from common.common_consts.common_enums import StrValueLabel


class MapPlayMemberRole(StrValueLabel):
    PARTICIPANT = 'participant', '참여자'
    ADMIN = 'admin', '관리자'


class MapPlayMemberDeactivateReason(StrValueLabel):
    SELF_DEACTIVATED = 'self_deactivated', '자발적 탈퇴'
    BANNED = 'banned', '추방' 