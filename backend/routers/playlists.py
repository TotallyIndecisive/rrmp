from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.db import SessionLocal
from backend.models.playlist import Playlist
from backend.models.playlist_track import PlaylistTrack
from backend.models.track import Track
from backend.schemas.playlist import (
    PlaylistCreate,
    PlaylistResponse,
    PlaylistDetailResponse,
    PlaylistTrackResponse,
    PlaylistReorderRequest,
    AddTrackToPlaylistRequest,
)

router = APIRouter(prefix="/playlists", tags=["playlists"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=PlaylistResponse)
def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db)):
    db_playlist = Playlist(name=playlist.name, created_at=datetime.utcnow())
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


@router.get("", response_model=List[PlaylistResponse])
def get_playlists(db: Session = Depends(get_db)):
    return db.query(Playlist).all()


@router.get("/{playlist_id}", response_model=PlaylistDetailResponse)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    playlist_tracks = (
        db.query(PlaylistTrack, Track)
        .join(Track, PlaylistTrack.track_id == Track.id)
        .filter(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.order)
        .all()
    )

    tracks = [
        PlaylistTrackResponse(
            id=pt.id,
            track_id=pt.track_id,
            order=pt.order,
            title=track.title,
            artist=track.artist,
            album=track.album,
            duration=track.duration,
            file_path=track.file_path,
        )
        for pt, track in playlist_tracks
    ]

    return PlaylistDetailResponse(
        id=playlist.id,
        name=playlist.name,
        created_at=playlist.created_at,
        tracks=tracks,
    )


@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id).delete()
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist deleted"}


@router.post("/{playlist_id}/tracks")
def add_track_to_playlist(
    playlist_id: int,
    request: AddTrackToPlaylistRequest,
    db: Session = Depends(get_db),
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    track = db.query(Track).filter(Track.id == request.track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    existing = (
        db.query(PlaylistTrack)
        .filter(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.track_id == request.track_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Track already in playlist")

    max_order = (
        db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id).count()
    )

    playlist_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=request.track_id,
        order=max_order,
    )
    db.add(playlist_track)
    db.commit()
    db.refresh(playlist_track)
    return {"message": "Track added", "id": playlist_track.id}


@router.delete("/{playlist_id}/tracks/{track_id}")
def remove_track_from_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
):
    playlist_track = (
        db.query(PlaylistTrack)
        .filter(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.track_id == track_id,
        )
        .first()
    )
    if not playlist_track:
        raise HTTPException(status_code=404, detail="Track not in playlist")

    db.delete(playlist_track)
    db.commit()
    return {"message": "Track removed"}


@router.patch("/{playlist_id}/reorder")
def reorder_playlist(
    playlist_id: int,
    request: PlaylistReorderRequest,
    db: Session = Depends(get_db),
):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    playlist_tracks = (
        db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id).all()
    )

    track_ids_set = set(request.track_ids)
    existing_track_ids = {pt.track_id for pt in playlist_tracks}

    if track_ids_set != existing_track_ids:
        raise HTTPException(
            status_code=400, detail="Track IDs must match playlist contents"
        )

    for order, track_id in enumerate(request.track_ids):
        playlist_track = (
            db.query(PlaylistTrack)
            .filter(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.track_id == track_id,
            )
            .first()
        )
        if playlist_track:
            playlist_track.order = order

    db.commit()
    return {"message": "Playlist reordered"}
