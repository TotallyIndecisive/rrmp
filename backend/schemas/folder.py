from pydantic import BaseModel
from datetime import datetime


class FolderBase(BaseModel):
    path: str


class FolderCreate(FolderBase):
    pass


class FolderResponse(FolderBase):
    id: int

    class Config:
        from_attributes = True
