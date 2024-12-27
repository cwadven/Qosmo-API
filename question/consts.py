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
