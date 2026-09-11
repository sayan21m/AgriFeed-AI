"""Visible-mould screen from a photo. Not aflatoxin ppb and not ingredient CP."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from smartfeed.paths import mould_vision

_VISION = None


def reload_vision() -> None:
    global _VISION
    _VISION = None


def mould_score(rgb: np.ndarray) -> dict:
    """rgb is uint8 HxWx3."""
    pix = rgb.reshape(-1, 3).astype(np.float32) / 255.0
    r, g, b = pix[:, 0], pix[:, 1], pix[:, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    diff = mx - mn
    s = np.where(mx == 0, 0, diff / np.clip(mx, 1e-6, None))
    v = mx
    h = np.zeros_like(v)
    mask = diff > 1e-6
    rc, gc, bc = r[mask], g[mask], b[mask]
    d = diff[mask]
    h_m = np.where(mx[mask] == rc, ((gc - bc) / d) % 6, 0)
    h_m = np.where(mx[mask] == gc, (bc - rc) / d + 2, h_m)
    h_m = np.where(mx[mask] == bc, (rc - gc) / d + 4, h_m)
    h[mask] = h_m * 60.0

    green = ((h > 70) & (h < 170) & (s > 0.18) & (v > 0.15)).mean()
    dark = ((v < 0.18) & (s < 0.35)).mean()
    white_fuzzy = ((v > 0.75) & (s < 0.18)).mean()
    score = float(min(1.0, 2.2 * green + 0.9 * dark + 0.5 * white_fuzzy))
    return {
        "green_frac": round(float(green), 4),
        "dark_frac": round(float(dark), 4),
        "white_frac": round(float(white_fuzzy), 4),
        "mould_score": round(score, 3),
        "flag": score >= 0.12,
    }


_hsv_mould_score = mould_score  # notebooks import the old private name


def _load_vision():
    global _VISION
    if _VISION is not None:
        return _VISION
    weights = mould_vision()
    if not weights.exists():
        _VISION = False
        return False
    import torch

    from smartfeed.dl_mould import make_vision

    blob = torch.load(weights, map_location="cpu", weights_only=False)
    model = make_vision(blob["kind"])
    model.load_state_dict(blob["state"])
    model.eval()
    _VISION = (blob["kind"], model)
    return _VISION


def assess_image(image_path: str | None = None, visible_mould: bool | None = None) -> dict:
    if image_path:
        path = Path(image_path)
        if not path.exists():
            return {"present": False, "note": f"Image not found: {path}"}
        from PIL import Image

        from smartfeed.dl_mould import predict_mould_proba

        rgb = np.asarray(Image.open(path).convert("RGB"))
        hsv = mould_score(rgb)
        vision = _load_vision()
        if vision:
            kind, model = vision
            proba = predict_mould_proba(model, rgb)
            flag = proba >= 0.5
            return {
                "present": True,
                "method": f"{kind}_over_hsv",
                "image": str(path),
                "cnn_mould_proba": round(proba, 3),
                "hsv": hsv,
                "mould_score": round(proba, 3),
                "flag": bool(flag),
                "note": (
                    f"{kind} on 32x32 (trained on synthetic cake/silage/mould, not Indian bags). "
                    "Not AFB1 µg/kg. HSV kept as a side check; it false-flags uniform green fodder."
                ),
            }
        return {
            "present": True,
            "method": "hsv_screen",
            "image": str(path),
            **hsv,
            "note": "Colour screen only. Petri-dish or bag mould ≠ AFB1 µg/kg.",
        }
    if visible_mould is None:
        return {"present": False, "note": "No photo and no farmer mould flag."}
    return {
        "present": True,
        "method": "farmer_flag",
        "mould_score": 1.0 if visible_mould else 0.0,
        "flag": bool(visible_mould),
        "note": "Farmer-reported visible mould. Do not convert this to ppb.",
    }
