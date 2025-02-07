from common.common_exceptions import CommonAPIException


class PlayAdminPermissionException(CommonAPIException):
    status_code = 403
    default_code = 'play-admin-permission-denied'
    default_detail = '해당 플레이의 admin만 이 작업을 수행할 수 있습니다.'


class PlayInviteCodeNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'play-invite-code-not-found'
    default_detail = '존재하지 않거나 이미 비활성화된 초대 코드입니다.'


class PlayMemberNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'play-member-not-found'
    default_detail = '존재하지 않거나 이미 비활성화된 멤버입니다.'


class PlayLastAdminException(CommonAPIException):
    status_code = 400
    default_code = 'play-last-admin'
    default_detail = '마지막 admin은 이 작업을 수행할 수 없습니다.'


class PlayAdminDeactivateException(CommonAPIException):
    status_code = 400
    default_code = 'play-admin-deactivate'
    default_detail = '다른 멤버가 있는 경우 admin 권한을 위임한 후에 탈퇴할 수 있습니다.' 