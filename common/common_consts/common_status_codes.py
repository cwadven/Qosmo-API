from common.common_consts.common_enums import StrValueLabel


class SuccessStatusCode(StrValueLabel):
    SUCCESS = ('success', '성공')


class ErrorStatusCode(StrValueLabel):
    INVALID_INPUT_HOME_LIST_PARAM_ERROR = ('home-invalid-input-param', '입력값을 다시 한번 확인해주세요.')
