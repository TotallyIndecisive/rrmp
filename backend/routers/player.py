import os
import sys
import random
import threading
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
    QueueRequest,
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
    _event_manager = None

_current_track_id: Optional[int] = None
_queue: list = []
_queue_index: int = -1
_shuffle: bool = False
_repeat: str = "off"
_folder_queue: list = []
_folder_queue_index: int = -1
_played_folder_tracks: set = set()
_queue_active: bool = False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _play_next_library_track():
    global _current_track_id, _shuffle, _repeat, _queue_active, _played_folder_tracks
    
    if _queue_active:
        print("Queue active - skipping library autoplay", file=sys.stderr)
        return
    
    print("Library autoplay: playing next folder track", file=sys.stderr)
    
    db = SessionLocal()
    try:
        if not _current_track_id:
            return
        
        tracks = db.query(Track).all()
        track_ids = [t.id for t in tracks]
        
        if not track_ids:
            return
        
        if _shuffle:
            available = [t for t in track_ids if t not in _played_folder_tracks]
            if not available:
                available = track_ids
            track_id = random.choice(available)
        else:
            try:
                current_pos = track_ids.index(_current_track_id)
            except ValueError:
                current_pos = -1
            
            if current_pos < len(track_ids) - 1:
                track_id = track_ids[current_pos + 1]
            elif _repeat == "all":
                track_id = track_ids[0]
            else:
                print("Library autoplay: end of folder, stopping", file=sys.stderr)
                if _media_player:
                    _media_player.stop()
                return
        
        _played_folder_tracks.add(track_id)
        
        track = db.query(Track).filter(Track.id == track_id).first()
        if track and _vlc_available and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        
        print(f"Library autoplay: {track_id}", file=sys.stderr)
    finally:
        db.close()


def on_track_end(event):
    global _queue_active
    if _queue_active:
        print("Queue mode active - not triggering library autoplay", file=sys.stderr)
        return
    print("Track ended, triggering library autoplay...", file=sys.stderr)
    threading.Timer(1.0, _play_next_library_track).start()


# Attach autoplay event
if _vlc_available:
    try:
        _event_manager = _media_player.event_manager()
        _event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, on_track_end)
        print("Autoplay event attached", file=sys.stderr)
    except Exception as e:
        print(f"Failed to attach autoplay event: {e}", file=sys.stderr)


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
        queue_active=_queue_active,
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
    global _queue_index, _current_track_id, _queue, _queue_active, _folder_queue, _folder_queue_index, _played_folder_tracks

    if _repeat == "one":
        track_id = _current_track_id if _current_track_id else _queue[0] if _queue else None
        if track_id:
            track = db.query(Track).filter(Track.id == track_id).first()
            if _vlc_available and track and os.path.exists(track.file_path):
                media = _instance.media_new(track.file_path)
                _media_player.set_media(media)
                _media_player.play()
            _current_track_id = track_id
        return {"message": "Playing (repeat one)", "track_id": track_id}

    # Priority 1: Queue is active and has unplayed tracks
    if _queue_active and _queue and _queue_index < len(_queue) - 1:
        if _shuffle:
            available = [t for t in _queue[_queue_index+1:] if t != _current_track_id]
            if not available:
                available = list(_queue)
            track_id = random.choice(available)
        else:
            _queue_index += 1
            track_id = _queue[_queue_index]
        
        track = db.query(Track).filter(Track.id == track_id).first()
        if _vlc_available and track and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        _current_track_id = track_id
        return {"message": "Playing next from queue", "track_id": track_id, "queue_active": True}

    # Queue exhausted - fall back to folder
    _queue_active = False
    _queue_index = -1
    
    if not _folder_queue:
        tracks = db.query(Track).all()
        _folder_queue = [t.id for t in tracks]

    # Add current track to played if not already
    if _current_track_id:
        _played_folder_tracks.add(_current_track_id)

    # Find next unplayed folder track
    available = [t for t in _folder_queue if t not in _played_folder_tracks]
    
    if available:
        if _shuffle:
            track_id = random.choice(available)
        else:
            # Find next after current position
            current_pos = _folder_queue.index(_current_track_id) if _current_track_id in _folder_queue else -1
            track_id = None
            for t in _folder_queue[current_pos+1:]:
                if t not in _played_folder_tracks:
                    track_id = t
                    break
            if not track_id:
                track_id = available[0]
        
        _folder_queue_index = _folder_queue.index(track_id)
        track = db.query(Track).filter(Track.id == track_id).first()
        if _vlc_available and track and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        _current_track_id = track_id
        return {"message": "Playing next from folder", "track_id": track_id, "queue_active": False}
    else:
        # No more unplayed tracks
        if _repeat == "all":
            _played_folder_tracks.clear()
            if _shuffle:
                track_id = random.choice(_folder_queue)
            else:
                _folder_queue_index = 0
                track_id = _folder_queue[0]
            track = db.query(Track).filter(Track.id == track_id).first()
            if _vlc_available and track and os.path.exists(track.file_path):
                media = _instance.media_new(track.file_path)
                _media_player.set_media(media)
                _media_player.play()
            _current_track_id = track_id
            return {"message": "Playing (repeat all)", "track_id": track_id, "queue_active": False}
        return {"message": "End of all tracks", "track_id": _current_track_id, "queue_active": False}


@router.post("/previous")
def previous_track(db: Session = Depends(get_db)):
    global _queue_index, _current_track_id, _queue, _queue_active, _folder_queue, _folder_queue_index, _played_folder_tracks

    if _repeat == "one":
        track_id = _current_track_id if _current_track_id else _queue[0] if _queue else None
        if track_id:
            track = db.query(Track).filter(Track.id == track_id).first()
            if _vlc_available and track and os.path.exists(track.file_path):
                media = _instance.media_new(track.file_path)
                _media_player.set_media(media)
                _media_player.play()
            _current_track_id = track_id
        return {"message": "Playing (repeat one)", "track_id": track_id}

    # Priority 1: Queue is active
    if _queue_active and _queue and _queue_index > 0:
        if _shuffle:
            available = [t for t in _queue[:_queue_index] if t != _current_track_id]
            if not available:
                available = list(_queue)
            track_id = random.choice(available)
        else:
            _queue_index -= 1
            track_id = _queue[_queue_index]
        
        track = db.query(Track).filter(Track.id == track_id).first()
        if _vlc_available and track and os.path.exists(track.file_path):
            media = _instance.media_new(track.file_path)
            _media_player.set_media(media)
            _media_player.play()
        _current_track_id = track_id
        return {"message": "Playing previous from queue", "track_id": track_id, "queue_active": True}

    # Fall back to folder
    if not _folder_queue:
        tracks = db.query(Track).all()
        _folder_queue = [t.id for t in tracks]

    # Previous in folder
    if _folder_queue_index > 0:
        _folder_queue_index -= 1
    elif _repeat == "all":
        _folder_queue_index = len(_folder_queue) - 1
    else:
        _folder_queue_index = 0
    
    track_id = _folder_queue[_folder_queue_index]
    track = db.query(Track).filter(Track.id == track_id).first()
    if _vlc_available and track and os.path.exists(track.file_path):
        media = _instance.media_new(track.file_path)
        _media_player.set_media(media)
        _media_player.play()
    _current_track_id = track_id
    return {"message": "Playing previous from folder", "track_id": track_id, "queue_active": _queue_active}


@router.post("/volume")
def set_volume(request: VolumeRequest):
    if _vlc_available:
        if not 0 <= request.level <= 100:
            raise HTTPException(status_code=400, detail="Volume must be 0-100")
        _media_player.audio_set_volume(request.level)
    return {"message": "Volume set", "level": request.level}


@router.post("/queue")
def set_queue(request: QueueRequest):
    global _queue, _queue_index, _queue_active
    _queue = [t.get('id') for t in request.queue if t.get('id')]
    _queue_index = 0
    _queue_active = len(_queue) > 0
    return {"message": "Queue updated", "queue_active": _queue_active, "queue_length": len(_queue)}
