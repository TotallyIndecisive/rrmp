import os
import vlc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.db import SessionLocal
from backend.models.folder import Folder
from backend.models.track import Track
from backend.models.recently_played import RecentlyPlayed
from backend.schemas.folder import FolderCreate, FolderResponse
from backend.schemas.track import TrackResponse

router = APIRouter(prefix="/library", tags=["library"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/folders", response_model=FolderResponse)
def add_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    existing = db.query(Folder).filter(Folder.path == folder.path).first()
    if existing:
        raise HTTPException(status_code=400, detail="Folder already exists")

    db_folder = Folder(path=folder.path)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


@router.get("/folders", response_model=List[FolderResponse])
def get_folders(db: Session = Depends(get_db)):
    return db.query(Folder).all()


@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    db.delete(folder)
    db.commit()
    return {"message": "Folder deleted"}


@router.post("/scan")
def scan_library(db: Session = Depends(get_db)):
    folders = db.query(Folder).all()
    audio_extensions = {".mp3", ".flac", ".wav", ".ogg", ".m4a"}
    scanned_count = 0
    skipped_count = 0

    for folder in folders:
        if not os.path.exists(folder.path):
            continue

        for root, _, files in os.walk(folder.path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in audio_extensions:
                    continue

                file_path = os.path.join(root, file)

                existing = db.query(Track).filter(Track.file_path == file_path).first()
                if existing:
                    skipped_count += 1
                    continue

                try:
                    metadata = extract_metadata(file_path)
                    track = Track(file_path=file_path, **metadata)
                    db.add(track)
                    scanned_count += 1
                except Exception:
                    skipped_count += 1

    db.commit()
    return {"scanned": scanned_count, "skipped": skipped_count}


def extract_metadata(file_path: str) -> dict:
    from mutagen import File as MutagenFile

    metadata = {
        "title": os.path.splitext(os.path.basename(file_path))[0],
        "artist": None,
        "album": None,
        "duration": None,
    }

    try:
        audio = MutagenFile(file_path)
        if audio is not None:
            if audio.tags:
                metadata["title"] = (
                    str(audio.tags.get("TIT2", metadata["title"]))
                    if audio.tags.get("TIT2")
                    else metadata["title"]
                )
                metadata["artist"] = (
                    str(audio.tags.get("TPE1", "")) if audio.tags.get("TPE1") else None
                )
                metadata["album"] = (
                    str(audio.tags.get("TALB", "")) if audio.tags.get("TALB") else None
                )
            if audio.info:
                metadata["duration"] = getattr(audio.info, "length", None)
    except Exception:
        pass

    return metadata


@router.get("/tracks", response_model=List[TrackResponse])
def get_tracks(
    search: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Track)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Track.title.ilike(search_filter)) | (Track.artist.ilike(search_filter))
        )
    if artist:
        query = query.filter(Track.artist.ilike(f"%{artist}%"))
    if album:
        query = query.filter(Track.album.ilike(f"%{album}%"))

    return query.all()


@router.get("/recent", response_model=List[TrackResponse])
def get_recent_tracks(db: Session = Depends(get_db)):
    recent = (
        db.query(RecentlyPlayed)
        .order_by(RecentlyPlayed.played_at.desc())
        .limit(20)
        .all()
    )
    track_ids = [r.track_id for r in recent]
    tracks = db.query(Track).filter(Track.id.in_(track_ids)).all()
    track_map = {t.id: t for t in tracks}
    return [track_map[tid] for tid in track_ids if tid in track_map]
