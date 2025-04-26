from common.common_consts.common_enums import StrValueLabel


class PushChannelType(StrValueLabel):
    DEFAULT = 'default', '기본'
    QUESTION_FEEDBACK = 'question_feedback', '문제 피드백'
    QUESTION_SOLVED_ALERT = 'question_solved_alert', '문제 해결 알림'
    ROLE_CHANGE = 'role_change', '역할 변경'
