from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UpdateNodePropertiesResponseDTO(BaseModel):
    id: int
    name: str
    title: str
    description: str
    background_image: str
    is_active: bool
    width: float
    height: float
    position_x: float
    position_y: float
    updated_at: datetime
    
    @classmethod
    def of(cls, node):
        """
        Node 모델 객체로부터 응답 DTO를 생성합니다.
        
        Args:
            node: 노드 모델 객체
            
        Returns:
            UpdateNodePropertiesResponseDTO 인스턴스
        """
        return cls(
            id=node.id,
            name=node.name,
            title=node.title,
            description=node.description,
            background_image=node.background_image,
            is_active=node.is_active,
            width=node.width,
            height=node.height,
            position_x=node.position_x,
            position_y=node.position_y,
            updated_at=node.updated_at
        )
