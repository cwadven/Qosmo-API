class NodeManagementService:
    def __init__(self, node_id: int):
        self.node_id = node_id

    def validate_node_meta_editable(self, member_id: int) -> None:
        node = Node.objects.filter(id=self.node_id).first()
        if not node:
            raise NodeNotFoundException()

        if node.meta.owner_id != member_id:
            raise ForbiddenAccessException()

    def update_node_position(self, position_x: float, position_y: float) -> Node:
        """노드 위치 업데이트"""
        node = Node.objects.filter(id=self.node_id).first()
        if not node:
            raise NodeNotFoundException()
        
        node.position_x = position_x
        node.position_y = position_y
        node.save()
        
        return node
        
    def update_node_properties(self, name=None, title=None, description=None, 
                              background_image=None, is_active=None, 
                              width=None, height=None) -> Node:
        """노드 속성 업데이트"""
        node = Node.objects.filter(id=self.node_id).first()
        if not node:
            raise NodeNotFoundException()
        
        # 제공된 값에 대해서만 업데이트
        if name is not None:
            node.name = name
            
        if title is not None:
            node.title = title
            
        if description is not None:
            node.description = description
            
        if background_image is not None:
            node.background_image = background_image
            
        if is_active is not None:
            node.is_active = is_active
            
        if width is not None:
            node.width = width
            
        if height is not None:
            node.height = height
            
        node.save()
        
        return node 