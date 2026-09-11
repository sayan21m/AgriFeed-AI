"""QR-based feed bag authenticity verification.

A feed mill or cooperative encodes bag details (manufacturer, batch,
packing date, declared CP, declared moisture) into a QR code.  The farmer
scans the QR, and the app compares declared values against what the
tables / sensors found.

The QR payload is a JSON dict encoded as URL-safe base64.  A production
system would sign or encrypt this; for the SIH26111 prototype it is plain
base64 so judges can inspect it.
"""

from __future__ import annotations

import base64
import json
from datetime import date, datetime


def generate_qr_payload(data: dict) -> str:
    """Encode bag metadata as a URL-safe base64 string for QR embedding.

    Expected keys (all optional except manufacturer):
        manufacturer, batch_no, pack_date (YYYY-MM-DD), expiry_date (YYYY-MM-DD),
        declared_cp_pct_dm, declared_moisture_pct, bis_license, feed_type
    """
    return base64.urlsafe_b64encode(json.dumps(data, ensure_ascii=False).encode()).decode()


def decode_qr_payload(payload: str) -> dict | None:
    """Decode a base64 QR payload back to a dict.  Returns None on failure."""
    text = (payload or "").strip()
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
    try:
        raw = base64.urlsafe_b64decode(text.encode())
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def verify_qr(payload: str, nutrition_result: dict | None = None) -> dict:
    """Compare QR-declared values against assess() nutrition results.

    Returns a dict with:
        decoded, verified, expired, warnings[], bag_info
    """
    bag = decode_qr_payload(payload)
    if bag is None:
        return {
            "present": True,
            "decoded": False,
            "verified": False,
            "warnings": ["Could not decode QR payload."],
        }

    warnings: list[str] = []
    expired = False

    # --- Expiry check ---
    expiry_str = bag.get("expiry_date")
    if expiry_str:
        try:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if expiry < date.today():
                expired = True
                warnings.append(f"Bag expired on {expiry_str}.")
        except ValueError:
            warnings.append(f"Invalid expiry date format: {expiry_str}")

    # --- CP mismatch ---
    cp_mismatch = False
    declared_cp = bag.get("declared_cp_pct_dm")
    if declared_cp is not None and nutrition_result:
        nutrients = (nutrition_result.get("nutrients_pct_dm") or {}).get("crude_protein_pct_dm")
        if nutrients and nutrients.get("mean") is not None:
            table_cp = nutrients["mean"]
            diff = abs(float(declared_cp) - float(table_cp))
            if diff > 5.0:
                cp_mismatch = True
                warnings.append(
                    f"Declared CP {declared_cp}% DM differs from table value "
                    f"{table_cp}% DM by {diff:.1f} percentage points."
                )

    # --- Moisture mismatch ---
    moisture_mismatch = False
    declared_moisture = bag.get("declared_moisture_pct")
    if declared_moisture is not None and nutrition_result:
        measured = nutrition_result.get("moisture_pct")
        if measured is not None:
            diff = abs(float(declared_moisture) - float(measured))
            if diff > 3.0:
                moisture_mismatch = True
                warnings.append(
                    f"Declared moisture {declared_moisture}% differs from "
                    f"measured {measured}% by {diff:.1f} points."
                )

    verified = not expired and not cp_mismatch and not moisture_mismatch and len(warnings) == 0

    return {
        "present": True,
        "decoded": True,
        "verified": verified,
        "expired": expired,
        "cp_mismatch": cp_mismatch,
        "moisture_mismatch": moisture_mismatch,
        "warnings": warnings,
        "bag_info": {
            "manufacturer": bag.get("manufacturer"),
            "batch_no": bag.get("batch_no"),
            "pack_date": bag.get("pack_date"),
            "expiry_date": bag.get("expiry_date"),
            "declared_cp_pct_dm": declared_cp,
            "declared_moisture_pct": declared_moisture,
            "bis_license": bag.get("bis_license"),
            "feed_type": bag.get("feed_type"),
            "ingredient": bag.get("ingredient"),
        },
        "note": "Prototype QR verification. Production systems should use signed payloads.",
    }
