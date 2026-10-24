"""Pure footprint semantics. No database, network, framework or model calls."""

import hashlib
import json
from datetime import UTC, datetime, timedelta


def capture_instant(day, wall_time: str | None, offset_minutes: int | None):
    if day is None or wall_time is None or offset_minutes is None:
        return None
    wall = datetime.fromisoformat(f"{day.isoformat()}T{wall_time}")
    return (wall - timedelta(minutes=offset_minutes)).replace(tzinfo=UTC)


def place_key(place) -> str:
    """Precision and coordinate system participate; same names alone never merge POIs."""
    values = [place.place_name, place.city, place.country, place.precision]
    if place.latitude is not None:
        values += [place.coordinate_system, round(place.latitude, 5), round(place.longitude, 5)]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def draft_expiry(received_at: datetime) -> datetime:
    return received_at + timedelta(hours=168)


def is_expired(photo, now: datetime) -> bool:
    if photo.state == "confirmed":
        return False
    deadline = photo.draft_expires_at or photo.ticket_expires_at
    return deadline <= now
