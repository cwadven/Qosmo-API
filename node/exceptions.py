from common.common_exceptions import CommonAPIException


class NodeNotFoundException(CommonAPIException):
    status_code = 404
    default_code = 'node-not-found'
    default_detail = '정상적인 Node 요청이 아닙니다.'
