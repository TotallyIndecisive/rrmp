from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from backend.db import SessionLocal
from backend.routers import library, player, playlists, metadata

app = FastAPI(title="RetroReel MP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Mount static files from the built frontend
dist_path = "/home/smckenzie/Tinkering/Projects/APR26/rrmp/frontend/dist"
app.mount(
    "/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets"
)
app.mount("/", StaticFiles(directory=dist_path, html=False), name="static")


# Catch-all for client-side routing (must be last)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Don't interfere with API routes
    if full_path.startswith(
        ("api/", "library", "player", "playlists", "metadata", "health")
    ):
        return {"detail": "Not found"}

    # For everything else, serve the SPA
    return FileResponse(os.path.join(dist_path, "index.html"))
