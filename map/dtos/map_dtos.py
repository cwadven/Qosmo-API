from pydantic import BaseModel

from map.models import Map


class MapDTO(BaseModel):
    map: Map
    is_subscribed: bool
