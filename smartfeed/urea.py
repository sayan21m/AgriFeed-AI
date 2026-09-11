"""4-DMAB yellow-area → urea estimate (Anitha 2022). BIS max 1% DM if urea is declared."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from smartfeed.names import normalize_name
from smartfeed.paths import PROCESSED

BIS_UREA_MAX_PCT = 1.0


def reload_urea() -> None:
    fit_urea_model.cache_clear()


def load_anitha() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "anitha_2022_urea_foldscope_yellow_area.csv")


def _cake_key(name: str) -> str | None:
    text = normalize_name(name)
    table = {
        "soybean meal": "Soyabean meal",
        "soyabean meal": "Soyabean meal",
        "groundnut cake": "Groundnut cake",
        "cottonseed cake undecorticated": "Un-decorticated cottonseed cake",
        "cottonseed cake": "Un-decorticated cottonseed cake",
    }
    for key, label in table.items():
        if key in text:
            return label
    return None


@lru_cache(maxsize=1)
def fit_urea_model() -> dict:
    """Ridge per cake on 3 calibration points, plus the observed yellow-area range."""
    df = load_anitha()
    models, ranges = {}, {}
    for cake, sub in df.groupby("oilseed_cake"):
        x = sub["yellow_area_pct_mean"].to_numpy(dtype=float)
        y = sub["urea_g_per_kg"].to_numpy(dtype=float)
        models[cake] = Ridge(alpha=0.1).fit(x.reshape(-1, 1), y)
        ranges[cake] = (float(x.min()), float(x.max()))
    global_x = df["yellow_area_pct_mean"].to_numpy(dtype=float)
    global_y = df["urea_g_per_kg"].to_numpy(dtype=float)
    models["__global__"] = Ridge(alpha=0.1).fit(global_x.reshape(-1, 1), global_y)
    ranges["__global__"] = (float(global_x.min()), float(global_x.max()))
    return {
        "models": models,
        "calibration_range_pct": ranges,
        "source": "Anitha 2022 ARCC foldscope yellow area",
    }


def assess_urea(
    yellow_area_pct: float | None,
    ingredient: str | None = None,
    model_bundle: dict | None = None,
) -> dict:
    if yellow_area_pct is None:
        return {"present": False, "note": "No 4-DMAB / foldscope yellow area. Urea is not visible on AS7265x."}
    bundle = model_bundle or fit_urea_model()
    cake = _cake_key(ingredient or "") or "__global__"
    model = bundle["models"].get(cake, bundle["models"]["__global__"])
    lo, hi = bundle["calibration_range_pct"].get(cake, bundle["calibration_range_pct"]["__global__"])

    area = float(yellow_area_pct)
    g_per_kg = max(0.0, float(model.predict(np.array([[area]], dtype=float))[0]))
    pct = g_per_kg / 10.0  # 10 g/kg = 1% DM

    # The curve only saw 1-10 g/kg. Report the edge value, not a straight-line guess.
    extrapolated = area < lo or area > hi
    if area > hi:
        g_at_edge = max(0.0, float(model.predict(np.array([[hi]], dtype=float))[0]))
        g_per_kg, pct = g_at_edge, g_at_edge / 10.0

    return {
        "present": True,
        "yellow_area_pct": area,
        "cake_curve": cake,
        "calibration_range_pct": [round(lo, 2), round(hi, 2)],
        "extrapolated": extrapolated,
        "urea_g_per_kg": round(g_per_kg, 2),
        "urea_pct_approx": round(pct, 2),
        "urea_pct_is_lower_bound": area > hi,
        "bis_max_pct": BIS_UREA_MAX_PCT,
        # Above the calibrated top the true load is >= 10 g/kg, i.e. at or past BIS.
        "over_bis": pct >= BIS_UREA_MAX_PCT or area > hi,
        "suspect": area >= lo,
        "note": (
            "Colour-area screen from Anitha 2022 (1-10 g/kg urea), not a Kjeldahl assay. "
            "Any yellow on a pure cake means added urea."
        ),
    }
