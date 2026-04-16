from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.db import SessionLocal

app = FastAPI(title="RetroReel MP")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}
