from typing import Optional

from pydantic import BaseModel


class MemberAnswerFileDto(BaseModel):
    id: Optional[int]
    name: Optional[str]
    url: Optional[str]
