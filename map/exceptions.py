from common.common_exceptions import CommonAPIException


class MapNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'map-not-found'
    default_detail = '정상적인 Map 요청이 아닙니다.'
