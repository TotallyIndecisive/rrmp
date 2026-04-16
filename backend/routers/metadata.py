import os
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.db import SessionLocal
from backend.models.track import Track
from backend.schemas.track import TrackMetadataResponse, TrackUpdate

router = APIRouter(prefix="/metadata", tags=["metadata"])

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets", "images"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_album_art(file_path: str) -> str | None:
    from mutagen import File as MutagenFile

    try:
        audio = MutagenFile(file_path)
        if audio is not None and audio.tags:
            for tag_name in ["APIC:", "cover", "Cover Art"]:
                artwork = audio.tags.get(tag_name)
                if artwork is not None:
                    if hasattr(artwork, "data"):
                        return base64.b64encode(artwork.data).decode("utf-8")
                    elif isinstance(artwork, list) and len(artwork) > 0:
                        item = artwork[0]
                        if hasattr(item, "data"):
                            return base64.b64encode(item.data).decode("utf-8")
    except Exception:
        pass
    return None


@router.get("/{track_id}", response_model=TrackMetadataResponse)
def get_track_metadata(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    album_art = get_album_art(track.file_path)

    return TrackMetadataResponse(
        id=track.id,
        file_path=track.file_path,
        title=track.title,
        artist=track.artist,
        album=track.album,
        duration=track.duration,
        custom_image_path=track.custom_image_path,
        album_art=album_art,
    )


@router.patch("/{track_id}/image")
async def update_track_image(
    track_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    os.makedirs(ASSETS_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"track_{track_id}{ext}"
    file_path = os.path.join(ASSETS_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    track.custom_image_path = file_path
    db.commit()

    return {"message": "Image updated", "custom_image_path": file_path}


@router.patch("/{track_id}")
def update_track_metadata(
    track_id: int,
    update: TrackUpdate,
    db: Session = Depends(get_db),
):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if update.title is not None:
        track.title = update.title
    if update.artist is not None:
        track.artist = update.artist
    if update.album is not None:
        track.album = update.album

    db.commit()
    db.refresh(track)

    return {"message": "Track updated", "track": track}
