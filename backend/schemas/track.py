from pydantic import BaseModel
from typing import Optional


class TrackBase(BaseModel):
    file_path: str
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[float] = None
    custom_image_path: Optional[str] = None


class TrackCreate(TrackBase):
    pass


class TrackResponse(BaseModel):
    id: int
    file_path: str
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[float] = None
    custom_image_path: Optional[str] = None

    class Config:
        from_attributes = True


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


class TrackMetadataResponse(BaseModel):
    id: int
    file_path: str
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[float] = None
    custom_image_path: Optional[str] = None
    album_art: Optional[str] = None

    class Config:
        from_attributes = True
