from common.common_criteria.cursor_criteria import CursorCriteria


class MapListCursorCriteria(CursorCriteria):
    cursor_keys = [
        'id__lte',
        'created_at__lt',
    ]
