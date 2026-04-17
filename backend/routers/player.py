import os
import sys
import random
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

# Initialize VLC - check if it works properly
_vlc_available = False
try:
    import vlc

    test_instance = vlc.Instance()
    test_player = test_instance.media_player_new()
    _instance = test_instance
    _media_player = test_player
    _vlc_available = True
    print("VLC initialized successfully - REAL MODE", file=sys.stderr)
except Exception as e:
    print(f"VLC initialization failed: {e} - using MOCK MODE", file=sys.stderr)
    _instance = None
    _media_player = None

_current_track_id: Optional[int] = None
_queue: list = []
_queue_index: int = -1
_shuffle: bool = False
_repeat: str = "off"


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
        shuffle=_shuffle,
        repeat=_repeat,
    )


@router.post("/play")
def play(request: PlayRequest, db: Session = Depends(get_db)):
    global _current_track_id, _queue, _queue_index

    track = db.query(Track).filter(Track.id == request.track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if _vlc_available and os.path.exists(track.file_path):
        print(f"Playing REAL: {track.file_path}", file=sys.stderr)
        media = _instance.media_new(track.file_path)
        _media_player.set_media(media)
        _media_player.play()
    else:
        print(f"Playing MOCK: {track.title}", file=sys.stderr)

    _current_track_id = track.id

    # Set up queue
    if not _queue:
        tracks = db.query(Track).all()
        _queue = [t.id for t in tracks]

    try:
        _queue_index = _queue.index(track.id)
    except ValueError:
        _queue.append(track.id)
        _queue_index = len(_queue) - 1

    recently_played = RecentlyPlayed(
        track_id=track.id,
        played_at=datetime.utcnow(),
    )
    db.add(recently_played)
    db.commit()

    return {"message": "Playing", "track_id": track.id}


@router.post("/pause")
def pause():
    if _vlc_available:
        _media_player.pause()
    return {"message": "Paused"}


@router.post("/resume")
def resume():
    if _vlc_available:
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
    if _vlc_available:
        _media_player.set_time(request.position_ms)
    return {"message": "Seeked", "position_ms": request.position_ms}


@router.post("/shuffle")
def toggle_shuffle():
    global _shuffle
    _shuffle = not _shuffle
    return {"message": f"Shuffle {'on' if _shuffle else 'off'}", "shuffle": _shuffle}


@router.post("/repeat")
def cycle_repeat():
    global _repeat
    if _repeat == "off":
        _repeat = "one"
    elif _repeat == "one":
        _repeat = "all"
    else:
        _repeat = "off"
    return {"message": f"Repeat: {_repeat}", "repeat": _repeat}


@router.post("/next")
def next_track(db: Session = Depends(get_db)):
    global _queue_index, _current_track_id, _queue

    if not _queue:
        tracks = db.query(Track).all()
        _queue = [t.id for t in tracks]
        _queue_index = 0

    # Handle repeat: one - replay same track
    if _repeat == "one":
        track_id = _current_track_id if _current_track_id else _queue[0]
        track = db.query(Track).filter(Track.id == track_id).first()
        if _vlc_available and track and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        _current_track_id = track_id
        return {"message": "Playing (repeat one)", "track_id": track_id}

    # Handle shuffle - choose random
    if _shuffle:
        available_tracks = [t for t in _queue if t != _current_track_id]
        if not available_tracks:
            available_tracks = _queue
        track_id = random.choice(available_tracks)
        _queue_index = _queue.index(track_id)
    else:
        # Normal next - handle repeat all or linear
        if _queue_index < len(_queue) - 1:
            _queue_index += 1
        elif _repeat == "all":
            _queue_index = 0  # Loop back to start
        else:
            return {"message": "End of queue", "track_id": _current_track_id}
        track_id = _queue[_queue_index]

    track = db.query(Track).filter(Track.id == track_id).first()

    if _vlc_available and track and os.path.exists(track.file_path):
        media = _instance.media_new(track.file_path)
        _media_player.set_media(media)
        _media_player.play()

    _current_track_id = track_id
    return {"message": "Playing next", "track_id": track_id}


@router.post("/previous")
def previous_track(db: Session = Depends(get_db)):
    global _queue_index, _current_track_id, _queue

    if not _queue:
        tracks = db.query(Track).all()
        _queue = [t.id for t in tracks]
        _queue_index = 0

    # Handle repeat: one - replay same track
    if _repeat == "one":
        track_id = _current_track_id if _current_track_id else _queue[0]
        track = db.query(Track).filter(Track.id == track_id).first()
        if _vlc_available and track and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        _current_track_id = track_id
        return {"message": "Playing (repeat one)", "track_id": track_id}

    # Handle shuffle - choose random
    if _shuffle:
        available_tracks = [t for t in _queue if t != _current_track_id]
        if not available_tracks:
            available_tracks = _queue
        track_id = random.choice(available_tracks)
        _queue_index = _queue.index(track_id)
    else:
        # Normal previous - handle wrap
        if _queue_index > 0:
            _queue_index -= 1
        elif _repeat == "all":
            _queue_index = len(_queue) - 1  # Loop to end
        else:
            _queue_index = 0
        track_id = _queue[_queue_index]

    track = db.query(Track).filter(Track.id == track_id).first()

    if _vlc_available and track and os.path.exists(track.file_path):
        media = _instance.media_new(track.file_path)
        _media_player.set_media(media)
        _media_player.play()

    _current_track_id = track_id
    return {"message": "Playing previous", "track_id": track_id}


@router.post("/volume")
def set_volume(request: VolumeRequest):
    if _vlc_available:
        if not 0 <= request.level <= 100:
            raise HTTPException(status_code=400, detail="Volume must be 0-100")
        _media_player.audio_set_volume(request.level)
    return {"message": "Volume set", "level": request.level}
