from sqlalchemy import Column, Integer, String, Float
from backend.db import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    album = Column(String, nullable=True)
    duration = Column(Float, nullable=True)
    custom_image_path = Column(String, nullable=True)
