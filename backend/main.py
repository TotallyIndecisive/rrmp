from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.db import SessionLocal
from backend.routers import library, player, playlists, metadata

app = FastAPI(title="RetroReel MP")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(library.router)
app.include_router(player.router)
app.include_router(playlists.router)
app.include_router(metadata.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
