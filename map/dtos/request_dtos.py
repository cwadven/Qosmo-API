from typing import Optional

from pydantic import BaseModel
from rest_framework.request import Request


class MapListRequestDTO(BaseModel):
    search: Optional[str] = None
    category_id: Optional[int] = None

    @classmethod
    def of(cls, request: Request) -> 'MapListRequestDTO':
        return cls(
            search=request.query_params.get('search'),
            category_id=request.query_params.get('category_id'),
        )


class MapSubscribedListRequestDTO(BaseModel):
    search: Optional[str] = None
    category_id: Optional[int] = None

    @classmethod
    def of(cls, request: Request) -> 'MapSubscribedListRequestDTO':
        return cls(
            search=request.query_params.get('search'),
            category_id=request.query_params.get('category_id'),
        )
