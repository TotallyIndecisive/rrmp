import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from backend.db import SessionLocal
from backend.models.track import Track
from backend.models.recently_played import RecentlyPlayed
from backend.schemas.player import (
    PlayerStatusResponse,
    PlayRequest,
    SeekRequest,
    VolumeRequest,
)

router = APIRouter(prefix="/player", tags=["player"])

try:
    import vlc

    _instance = vlc.Instance()
    _media_player = _instance.media_player_new()
    _vlc_available = True
    print("VLC instance created successfully")
except Exception as e:
    print(f"Failed to initialize VLC: {e}")
    _vlc_available = False
    _media_player = None

_current_track_id: Optional[int] = None
_queue: list = []
_queue_index: int = -1


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_position_ms() -> int:
    if _media_player:
        return int(_media_player.get_time())
    return 0


def get_duration_ms() -> int:
    if _media_player:
        return int(_media_player.get_length())
    return 0


def get_is_playing() -> bool:
    if _media_player:
        return _media_player.is_playing() == 1
    return False


@router.get("/status", response_model=PlayerStatusResponse)
def get_status():
    return PlayerStatusResponse(
        track_id=_current_track_id,
        is_playing=get_is_playing(),
        position_ms=get_position_ms(),
        duration_ms=get_duration_ms(),
        volume=_media_player.audio_get_volume() if _media_player else 100,
    )


@router.post("/play")
def play(request: PlayRequest, db: Session = Depends(get_db)):
    global _current_track_id

    if not _vlc_available:
        # Mock mode: just update state
        track = db.query(Track).filter(Track.id == request.track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        _current_track_id = track.id
        recently_played = RecentlyPlayed(
            track_id=track.id,
            played_at=datetime.utcnow(),
        )
        db.add(recently_played)
        db.commit()
        return {"message": "Playing (mock)", "track_id": track.id}

    track = db.query(Track).filter(Track.id == request.track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if not os.path.exists(track.file_path):
        raise HTTPException(
            status_code=400, detail=f"File not found: {track.file_path}"
        )

    print(f"Playing file: {track.file_path}")
    media = _instance.media_new(track.file_path)
    _media_player.set_media(media)
    _media_player.play()

    _current_track_id = track.id

    recently_played = RecentlyPlayed(
        track_id=track.id,
        played_at=datetime.utcnow(),
    )
    db.add(recently_played)
    db.commit()

    return {"message": "Playing", "track_id": track.id}


@router.post("/pause")
def pause():
    if not _vlc_available:
        return {"message": "Paused (mock)"}
    _media_player.pause()
    return {"message": "Paused"}


@router.post("/resume")
def resume():
    if not _vlc_available:
        return {"message": "Resumed (mock)"}
    _media_player.play()
    return {"message": "Resumed"}


@router.post("/stop")
def stop():
    global _current_track_id
    if _media_player:
        _media_player.stop()
    _current_track_id = None
    return {"message": "Stopped"}


@router.post("/seek")
def seek(request: SeekRequest):
    if not _vlc_available:
        return {"message": "Seeked (mock)", "position_ms": request.position_ms}
    _media_player.set_time(request.position_ms)
    return {"message": "Seeked", "position_ms": request.position_ms}


@router.post("/next")
def next_track(db: Session = Depends(get_db)):
    global _queue_index, _current_track_id

    if not _vlc_available:
        # Mock mode: just move to next track in queue
        tracks = db.query(Track).all()
        if not tracks:
            raise HTTPException(status_code=400, detail="No tracks available")
        if not _queue:
            _queue = [t.id for t in tracks]
            _queue_index = 0
        else:
            if _queue_index < len(_queue) - 1:
                _queue_index += 1
            else:
                _queue_index = 0
        _current_track_id = _queue[_queue_index]
        return {"message": "Playing next (mock)", "track_id": _current_track_id}

    if not _queue:
        tracks = db.query(Track).all()
        _queue.extend([t.id for t in tracks])

    if _queue_index < len(_queue) - 1:
        _queue_index += 1
        track_id = _queue[_queue_index]
        track = db.query(Track).filter(Track.id == track_id).first()
        if track:
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
            _current_track_id = track.id
            return {"message": "Playing next", "track_id": track.id}

    raise HTTPException(status_code=400, detail="No next track")


@router.post("/previous")
def previous_track(db: Session = Depends(get_db)):
    global _queue_index, _current_track_id

    if not _vlc_available:
        # Mock mode: just move to previous track in queue
        tracks = db.query(Track).all()
        if not tracks:
            raise HTTPException(status_code=400, detail="No tracks available")
        if not _queue:
            _queue = [t.id for t in tracks]
            _queue_index = 0
        else:
            if _queue_index > 0:
                _queue_index -= 1
            else:
                _queue_index = len(_queue) - 1
        _current_track_id = _queue[_queue_index]
        return {"message": "Playing previous (mock)", "track_id": _current_track_id}

    if not _queue:
        tracks = db.query(Track).all()
        _queue.extend([t.id for t in tracks])

    if _queue_index > 0:
        _queue_index -= 1
        track_id = _queue[_queue_index]
        track = db.query(Track).filter(Track.id == track_id).first()
        if track:
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
            _current_track_id = track.id
            return {"message": "Playing previous", "track_id": track.id}

    raise HTTPException(status_code=400, detail="No previous track")


@router.post("/volume")
def set_volume(request: VolumeRequest):
    if not _vlc_available:
        return {"message": "Volume set (mock)", "level": request.level}
    if not 0 <= request.level <= 100:
        raise HTTPException(status_code=400, detail="Volume must be 0-100")

    _media_player.audio_set_volume(request.level)
    return {"message": "Volume set", "level": request.level}
