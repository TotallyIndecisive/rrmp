from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PlaylistBase(BaseModel):
    name: str


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistTrackResponse(BaseModel):
    id: int
    track_id: int
    order: int
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None

    class Config:
        from_attributes = True


class PlaylistResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistDetailResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    tracks: List[PlaylistTrackResponse]

    class Config:
        from_attributes = True


class PlaylistReorderRequest(BaseModel):
    track_ids: List[int]


class AddTrackToPlaylistRequest(BaseModel):
    track_id: int
