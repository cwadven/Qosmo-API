from typing import Optional

from pydantic import BaseModel
from rest_framework.request import Request


class MapListRequestDTO(BaseModel):
    search: Optional[str] = None

    @classmethod
    def of(cls, request: Request) -> 'MapListRequestDTO':
        return cls(
            search=request.query_params.get('search')
        )
