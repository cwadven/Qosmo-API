from common.common_criteria.cursor_criteria import CursorCriteria


class MapListCursorCriteria(CursorCriteria):
    cursor_keys = [
        'id__lt',
    ]


class MapSubscriptionListCursorCriteria(CursorCriteria):
    cursor_keys = [
        'id__lt',
        'updated_at__lte',
    ]


class MyMapListCursorCriteria(CursorCriteria):
    cursor_keys = [
        'id__lt',
    ]
