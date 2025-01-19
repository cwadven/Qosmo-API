from common.common_consts.common_enums import StrValueLabel


class QuestionType(StrValueLabel):
    """
    문제 타입
    """
    TEXT = ('text', '텍스트')
    FILE = ('file', '파일')


class ValidationType(StrValueLabel):
    """
    정답 검증 방식
    """
    TEXT_EXACT = ('text_exact', '텍스트 정확일치')
    TEXT_CONTAINS = ('text_contains', '텍스트 포함')
    REGEX = ('regex', '정규식')
    MANUAL = ('manual', '관리자 수동 평가')


class QuestionInvalidInputResponseErrorStatus(StrValueLabel):
    """
    Question 입력값 검증 실패 응답 코드
    """
    INVALID_INPUT_ANSWER_PARAM_ERROR_400 = ('40040002', '입력값을 확인해주세요.')


class AnswerStatus(StrValueLabel):
    """
    답변 상태
    """
    SUCCESS = ('success', '정답')
    FAILED = ('failed', '오답')
    PENDING = ('pending', '검토중')
