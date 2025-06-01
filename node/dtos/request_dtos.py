from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError

from common.common_exceptions import PydanticAPIException
from common.common_consts.common_error_messages import InvalidInputResponseErrorStatus


class UpdateNodePropertiesRequestDTO(BaseModel):
    name: Optional[str] = Field(None, description="노드 이름")
    title: Optional[str] = Field(None, description="노드 제목")
    description: Optional[str] = Field(None, description="노드 설명")
    background_image: Optional[str] = Field(None, description="배경 이미지 URL")
    is_active: Optional[bool] = Field(None, description="활성화 여부")
    width: Optional[float] = Field(None, description="노드 너비")
    height: Optional[float] = Field(None, description="노드 높이")
    position_x: Optional[float] = Field(None, description="X 좌표 위치")
    position_y: Optional[float] = Field(None, description="Y 좌표 위치")

    @classmethod
    def of(cls, request):
        data = request.data.copy()
        
        # 문자열로 받은 is_active를 boolean으로 변환
        if 'is_active' in data and isinstance(data['is_active'], str):
            data['is_active'] = data['is_active'].lower() in ['true', '1', 't', 'y', 'yes']
            
        dto = cls(**data)
        
        # 최소한 하나의 필드가 제공되었는지 검증
        if not dto.has_any_field():
            raise PydanticAPIException(
                status_code=400,
                error_summary="최소한 하나의 속성이 필요합니다.",
                error_code=InvalidInputResponseErrorStatus.INVALID_UPDATE_NODE_PROPERTIES_INPUT_DATA_400.value,
                errors={
                    "properties": ["최소한 하나의 속성이 필요합니다."]
                }
            )
            
        return dto
        
    def has_any_field(self) -> bool:
        """최소한 하나의 필드가 제공되었는지 확인"""
        return any(getattr(self, field) is not None for field in self.model_fields)
