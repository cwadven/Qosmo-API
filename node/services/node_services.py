from typing import List

from django.db.models import QuerySet

from map.models import Node, NodeCompletedHistory


def get_nodes_by_map_id(map_id: int) -> List[Node]:
    return Node.objects.filter(
        map_id=map_id,
        is_deleted=False,
    ).select_related(
        'map',
    )


def get_member_completed_node_histories(member_id: int, map_id: int) -> QuerySet[NodeCompletedHistory]:
    return NodeCompletedHistory.objects.filter(
        map_id=map_id,
        member_id=member_id,
    ).select_related(
        'node__map',
    )
