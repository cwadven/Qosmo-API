from common.common_consts.common_enums import StrValueLabel


class GraphNodeStatus(StrValueLabel):
    COMPLETED = ('READY', '해금')
    IN_PROGRESS = ('IN_PROGRESS', '진행중')
    LOCKED = ('FAIL', '잠김')
    DEACTIVATED = ('DEACTIVATED', '비활성화')
