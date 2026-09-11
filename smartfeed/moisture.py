"""Moisture sensor: convert % DM tables to as-fed. Does not measure protein."""

from __future__ import annotations


def dry_matter_pct(moisture_pct: float) -> float:
    return round(100.0 - float(moisture_pct), 2)


def as_fed(value_pct_dm: float | None, moisture_pct: float | None) -> float | None:
    if value_pct_dm is None or moisture_pct is None:
        return None
    return round(float(value_pct_dm) * (1.0 - float(moisture_pct) / 100.0), 2)


def as_fed_span(span: dict | None, moisture_pct: float | None) -> dict | None:
    if not span or moisture_pct is None:
        return None
    return {
        "mean": as_fed(span.get("mean"), moisture_pct),
        "min": as_fed(span.get("min"), moisture_pct),
        "max": as_fed(span.get("max"), moisture_pct),
    }


def assess_moisture(moisture_pct: float | None, form: str | None = None) -> dict:
    if moisture_pct is None:
        return {"present": False, "note": "No moisture reading. Tables stay on a % DM basis."}
    m = float(moisture_pct)
    dm = dry_matter_pct(m)
    flags = []
    if form == "silage":
        if m < 60:
            flags.append("silage_too_dry_risk_heat")
        elif m > 75:
            flags.append("silage_too_wet_risk_effluent")
        else:
            flags.append("silage_dm_in_typical_band")
    else:
        if m > 14:
            flags.append("dry_feed_above_safe_store_moisture")
        if m > 11 and form == "compounded":
            flags.append("above_bis_moisture_max_11")
    return {
        "present": True,
        "moisture_pct": m,
        "dry_matter_pct": dm,
        "flags": flags,
        "note": "Moisture converts % DM to as-fed. It is not crude protein.",
    }
