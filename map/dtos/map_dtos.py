from pydantic import (
    BaseModel,
    ConfigDict,
)

from map.models import Map


class MapDTO(BaseModel):
    map: Map
    is_subscribed: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)
