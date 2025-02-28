from common.common_exceptions import CommonAPIException


class PlayAdminPermissionException(CommonAPIException):
    status_code = 403
    default_code = 'play-admin-permission-denied'
    default_detail = '해당 플레이의 admin만 이 작업을 수행할 수 있습니다.'


class PlayAdminCannotChangeRolePermissionException(CommonAPIException):
    status_code = 403
    default_code = 'play-admin-cannot-change-role-permission-denied'
    default_detail = '관리자의 권한은 수정할 수 없습니다.'


class PlayMaximumLimitExceededException(CommonAPIException):
    status_code = 400
    default_code = 'play-maximum-limit-exceeded'
    default_detail = '한 Map에 대해 최대 3개의 플레이에만 참여할 수 있습니다.'


class PlayInviteCodeNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'play-invite-code-not-found'
    default_detail = '존재하지 않거나 이미 비활성화된 초대 코드입니다.'


class AlreadyPlayMemberException(CommonAPIException):
    status_code = 400
    default_code = 'play-already-member'
    default_detail = '이미 플레이 멤버입니다.'


class PlayMemberFromInviteBannedException(CommonAPIException):
    status_code = 400
    default_code = 'play-member-banned'
    default_detail = '이 초대 코드로는 더 이상 참여할 수 없습니다.'


class PlayMemberInviteCodeMaxUseException(CommonAPIException):
    status_code = 400
    default_code = 'play-member-invite-code-max-use'
    default_detail = '초대 코드 사용 횟수를 초과했습니다.'


class PlayMemberInvalidInviteCodeException(CommonAPIException):
    status_code = 400
    default_code = 'play-member-invalid-invite-code'
    default_detail = '유효하지 않은 초대 코드입니다.'


class PlayMemberAlreadyDeactivatedInviteCodeException(CommonAPIException):
    status_code = 400
    default_code = 'play-member-already-deactivated-invite-code'
    default_detail = '초대 코드가 만료되었습니다.'


class PlayMemberNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'play-member-not-found'
    default_detail = '존재하지 않거나 이미 비활성화된 멤버입니다.'


class PlayMemberNoPermissionException(CommonAPIException):
    status_code = 403
    default_code = 'play-member-no-permission'
    default_detail = '해당 멤버는 이 작업을 수행할 수 없습니다.'


class PlayLastAdminException(CommonAPIException):
    status_code = 400
    default_code = 'play-last-admin'
    default_detail = '마지막 admin은 이 작업을 수행할 수 없습니다.'


class PlayAdminDeactivateException(CommonAPIException):
    status_code = 400
    default_code = 'play-admin-deactivate'
    default_detail = '다른 멤버가 있는 경우 admin 권한을 위임한 후에 탈퇴할 수 있습니다.'


class PlayMemberAlreadyRoleException(CommonAPIException):
    status_code = 400
    default_code = 'play-member-already-role'
    default_detail = '이미 해당 역할입니다.'
