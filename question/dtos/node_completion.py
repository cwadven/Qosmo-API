from typing import List

from pydantic import BaseModel, Field

from map.models import Node
from map.models.arrow_progress import ArrowProgress
from map.models.node_history import NodeCompletedHistory


class NodeCompletionResultDto(BaseModel):
    new_arrow_progresses: List[ArrowProgress] = Field(default=[], description="생성된 ArrowProgress 목록 (id 미포함)")
    new_completed_node_histories: List[NodeCompletedHistory] = Field(default=[], description="생성된 NodeCompletedHistory 목록 (id 미포함)")
    activated_nodes: List[Node] = Field(default=[], description="in_progress 된 Node id 목록")
