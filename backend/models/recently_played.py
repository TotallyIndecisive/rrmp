from sqlalchemy import Column, Integer, ForeignKey, DateTime
from backend.db import Base


class RecentlyPlayed(Base):
    __tablename__ = "recently_played"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime, nullable=False)
