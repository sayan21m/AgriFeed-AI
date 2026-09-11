"""256-band forage NIR from Marcondes 2025. Not AS7265x (410–940 nm, 18 ch)."""

from __future__ import annotations

import numpy as np
import joblib
from scipy.signal import savgol_filter

from smartfeed.paths import nir_joblib

_BUNDLE = None


def load_nir():
    global _BUNDLE
    if _BUNDLE is None:
        _BUNDLE = joblib.load(nir_joblib())
    return _BUNDLE


def reload_nir() -> None:
    global _BUNDLE
    _BUNDLE = None


def _snv(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def _savgol1(X: np.ndarray) -> np.ndarray:
    return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)


def _prep(vec: np.ndarray, name: str) -> np.ndarray:
    xs = _snv(vec)
    if "SG1" in name:
        xs = _savgol1(xs)
    return xs


def assess_nir(absorbance) -> dict:
    if absorbance is None:
        return {"present": False, "note": "No spectrum."}
    vec = np.asarray(absorbance, dtype=float).reshape(1, -1)
    if vec.shape[1] == 18:
        return {
            "present": True,
            "used": False,
            "note": (
                "Got 18 AS7265x channels. No Indian paired calibration exists. "
                "Not scoring CP from this chip."
            ),
        }
    bundle = load_nir()
    n = len(bundle["wavelengths_nm"])
    if vec.shape[1] != n:
        return {
            "present": True,
            "used": False,
            "note": f"Need {n} bands (890–1707 nm) or 18 AS7265x channels, got {vec.shape[1]}.",
        }
    pred = {
        "cp_pct_dm": float(bundle["cp_model"].predict(_prep(vec, bundle["cp_winner"])).ravel()[0]),
        "ndf_pct_dm": float(bundle["ndf_model"].predict(_prep(vec, bundle["ndf_winner"])).ravel()[0]),
        "adf_pct_dm": float(bundle["adf_model"].predict(_prep(vec, bundle["adf_winner"])).ravel()[0]),
    }
    return {
        "present": True,
        "used": True,
        "predictions": {k: round(v, 2) for k, v in pred.items()},
        "matrix": bundle["disclaimer"],
    }
