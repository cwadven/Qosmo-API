from common.common_exceptions import CommonAPIException


class QuestionNotFoundException(CommonAPIException):
    status_code = 404
    default_code = '40440001'
    default_detail = 'Question을 찾을 수 없습니다.'


class AnswerPermissionDeniedException(CommonAPIException):
    status_code = 403
    default_code = '40340001'
    default_detail = '답변을 제출할 권한이 없습니다.'


class AnswerNotFoundException(CommonAPIException):
    status_code = 404
    default_code = '40440002'
    default_detail = '답변이 존재하지 않습니다.'
