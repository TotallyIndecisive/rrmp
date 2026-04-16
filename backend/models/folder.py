from sqlalchemy import Column, Integer, String
from backend.db import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
