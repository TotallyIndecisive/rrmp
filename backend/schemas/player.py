from pydantic import BaseModel
from typing import Optional, List


class PlayerStatusResponse(BaseModel):
    track_id: Optional[int] = None
    is_playing: bool = False
    position_ms: int = 0
    duration_ms: int = 0
    volume: int = 100
    shuffle: bool = False
    repeat: str = "off"
    queue_active: bool = False


class PlayRequest(BaseModel):
    track_id: int


class SeekRequest(BaseModel):
    position_ms: int


class VolumeRequest(BaseModel):
    level: int


class QueueRequest(BaseModel):
    queue: List[dict]
