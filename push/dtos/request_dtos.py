from pydantic import (
    BaseModel,
    Field,
)


class PutPushMapPlayMemberActiveRequest(BaseModel):
    is_active: bool = Field(description='활성화 여부')
    push_map_play_member_ids: list[int] = Field(description='푸시 설정 ID 리스트')
