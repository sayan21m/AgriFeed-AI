"""Last reading from the village ESP32 kit.

The phone owns the photo and the ingredient name. The board only posts moisture,
optional pH, and 18 AS7265x counts. Those 18 counts are never turned into CP.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.sensors.as7265x import CHANNELS_NM

AS7265X_N = 18

_lock = Lock()
_latest: dict | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_reading(payload: dict) -> dict:
    spectrum = payload.get("as7265x")
    if spectrum is not None:
        if not isinstance(spectrum, list) or len(spectrum) != AS7265X_N:
            raise ValueError(f"as7265x must be {AS7265X_N} numbers, got {None if spectrum is None else len(spectrum)}")
        spectrum = [float(x) for x in spectrum]

    reading = {
        "device_id": str(payload.get("device_id") or "smartfeed-kit"),
        "received_at": _now(),
        "moisture_pct": payload.get("moisture_pct"),
        "ph": payload.get("ph"),
        "as7265x": spectrum,
        "as7265x_channels_nm": list(CHANNELS_NM) if spectrum is not None else None,
        "moisture_raw": payload.get("moisture_raw"),
        "ph_raw": payload.get("ph_raw"),
        "note": (
            "18 AS7265x counts are a colour snapshot, not Indian crude protein. "
            "Take the mould photo on the phone."
        ),
    }
    global _latest
    with _lock:
        _latest = reading
    return reading


def latest_reading() -> dict | None:
    with _lock:
        return None if _latest is None else dict(_latest)
