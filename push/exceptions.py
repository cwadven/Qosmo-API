from common.common_exceptions import CommonAPIException


class PushMapPlayMemberNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'push-map-play-member-not-found'
    default_detail = '활성화된 푸시 알림 설정이 없습니다.'
