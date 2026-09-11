"""Reject impossible sensor readings before they become farmer advice.

A disconnected moisture probe or a mistyped pH must not turn into a confident
recommendation. Anything outside physical range raises; anything merely unusual
is returned as a warning the caller can show.
"""

from __future__ import annotations

RANGES = {
    "moisture_pct": (0.0, 100.0),
    "ph": (0.0, 14.0),
    "urea_yellow_area_pct": (0.0, 100.0),
    "aia_pct": (0.0, 100.0),
    "grit_settled_ml": (0.0, 1000.0),
    "sample_g": (0.1, 10000.0),
}

# Outside these the reading is possible but almost certainly a bad measurement.
PLAUSIBLE = {
    "moisture_pct": (2.0, 95.0),
    "ph": (3.0, 9.0),
}


class SensorRangeError(ValueError):
    """A reading that cannot physically be right."""


def check(name: str, value: float | None) -> float | None:
    if value is None:
        return None
    val = float(value)
    if val != val:  # NaN
        raise SensorRangeError(f"{name} is not a number")
    lo, hi = RANGES[name]
    if not lo <= val <= hi:
        raise SensorRangeError(f"{name}={val} is outside the valid range {lo}-{hi}")
    return val


def warnings_for(readings: dict) -> list[str]:
    out = []
    for name, (lo, hi) in PLAUSIBLE.items():
        val = readings.get(name)
        if val is not None and not lo <= float(val) <= hi:
            out.append(f"{name}={val} is outside the usual {lo}-{hi} band — check the sensor.")
    return out


def check_all(readings: dict) -> list[str]:
    """Validate every known reading, then return the soft warnings."""
    for name in RANGES:
        if name in readings:
            check(name, readings[name])
    return warnings_for(readings)
