from common.common_consts.common_enums import StrValueLabel


class MapInvalidInputResponseErrorStatus(StrValueLabel):
    INVALID_INPUT_MAP_LIST_PARAM_ERROR_400 = (
        'invalid-map-list-input',
        '입력값을 다시 한번 확인해주세요.',
    )
    INVALID_INPUT_FEEDBACK_ANSWERS_ERROR_400 = (
        'invalid-feedback-input',
        '입력값을 다시 한번 확인해주세요.',
    )
