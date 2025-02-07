from common.common_consts.common_enums import StrValueLabel


class PlayInvalidInputResponseErrorStatus(StrValueLabel):
    INVALID_INPUT_CREATE_MAP_PLAY_ERROR_400 = 'INVALID_INPUT_CREATE_MAP_PLAY_ERROR_400', '맵 플레이 생성 입력값이 올바르지 않습니다.'
    INVALID_INPUT_CREATE_INVITE_CODE_ERROR_400 = 'INVALID_INPUT_CREATE_INVITE_CODE_ERROR_400', '초대 코드 생성 입력값이 올바르지 않습니다.'
    INVALID_INPUT_CHANGE_ROLE_ERROR_400 = 'INVALID_INPUT_CHANGE_ROLE_ERROR_400', '역할 변경 입력값이 올바르지 않습니다.'
    INVALID_INPUT_BAN_MEMBER_ERROR_400 = 'INVALID_INPUT_BAN_MEMBER_ERROR_400', '멤버 추방 입력값이 올바르지 않습니다.'
    FORBIDDEN_NOT_ADMIN_ERROR_403 = 'FORBIDDEN_NOT_ADMIN_ERROR_403', '해당 플레이의 admin만 이 작업을 수행할 수 있습니다.' 