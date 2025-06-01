from map.models import Node
from node.exceptions import NodeNotFoundException
from typing import Optional


class NodeManagementService:
    def __init__(self, node_id: int):
        self.node_id = node_id

    def validate_node_meta_editable(self, member_id) -> None:
        try:
            node = Node.objects.get(
                id=self.node_id,
                is_deleted=False,
            )
        except Node.DoesNotExist:
            raise NodeNotFoundException()

        if member_id != node.map.created_by_id:
            raise NodeNotFoundException()

    def update_node_position(self, position_x: float, position_y: float) -> Node:
        """
        노드의 위치를 업데이트합니다.
        
        Args:
            position_x: 새로운 X 좌표
            position_y: 새로운 Y 좌표
            
        Returns:
            업데이트된 노드 객체
        """
        try:
            node = Node.objects.get(
                id=self.node_id,
                is_deleted=False,
            )
        except Node.DoesNotExist:
            raise NodeNotFoundException()
            
        # 위치 업데이트
        node.position_x = position_x
        node.position_y = position_y
        node.save(
            update_fields=['position_x', 'position_y', 'updated_at']
        )
        
        return node

    def update_node_properties(self, 
                               name: Optional[str] = None,
                               title: Optional[str] = None,
                               description: Optional[str] = None,
                               background_image: Optional[str] = None,
                               is_active: Optional[bool] = None,
                               width: Optional[float] = None,
                               height: Optional[float] = None,
                               position_x: Optional[float] = None,
                               position_y: Optional[float] = None) -> Node:
        """
        노드의 속성들을 업데이트합니다.
        
        Args:
            name: 노드 이름
            title: 노드 제목
            description: 노드 설명
            background_image: 배경 이미지 URL
            is_active: 활성화 여부
            width: 노드 너비
            height: 노드 높이
            position_x: X 좌표 위치
            position_y: Y 좌표 위치
            
        Returns:
            업데이트된 노드 객체
        """
        try:
            node = Node.objects.get(
                id=self.node_id,
                is_deleted=False,
            )
        except Node.DoesNotExist:
            raise NodeNotFoundException()
            
        # 업데이트할 필드 목록
        update_fields = ['updated_at']
        
        # 각 필드 업데이트 (None이 아닐 경우에만)
        if name is not None:
            node.name = name
            update_fields.append('name')
            
        if title is not None:
            node.title = title
            update_fields.append('title')
            
        if description is not None:
            node.description = description
            update_fields.append('description')
            
        if background_image is not None:
            node.background_image = background_image
            update_fields.append('background_image')
            
        if is_active is not None:
            node.is_active = is_active
            update_fields.append('is_active')
            
        if width is not None:
            node.width = width
            update_fields.append('width')
            
        if height is not None:
            node.height = height
            update_fields.append('height')
            
        if position_x is not None:
            node.position_x = position_x
            update_fields.append('position_x')
            
        if position_y is not None:
            node.position_y = position_y
            update_fields.append('position_y')
            
        # 변경사항이 있을 경우에만 저장
        if len(update_fields) > 1:  # 'updated_at'은 항상 포함되므로 1보다 커야 함
            node.save(update_fields=update_fields)
        
        return node
