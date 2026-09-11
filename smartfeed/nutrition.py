"""Name → Indian table range, or TF-IDF fallback from the trained joblib."""

from __future__ import annotations

from difflib import get_close_matches

import joblib
import pandas as pd

from smartfeed.moisture import as_fed_span
from smartfeed.names import enrich, normalize_name
from smartfeed.paths import nutrition_joblib

_BUNDLE = None


def load_nutrition():
    global _BUNDLE
    if _BUNDLE is None:
        _BUNDLE = joblib.load(nutrition_joblib())
        _BUNDLE["lookup_df"] = pd.DataFrame(_BUNDLE["lookup"])
    return _BUNDLE


def reload_nutrition() -> None:
    global _BUNDLE
    _BUNDLE = None


def _span(row: dict, stem: str):
    mean = row.get(f"{stem}_mean")
    if mean is None or (isinstance(mean, float) and pd.isna(mean)):
        return None
    return {
        "mean": round(float(mean), 2),
        "min": round(float(row.get(f"{stem}_min")), 2),
        "max": round(float(row.get(f"{stem}_max")), 2),
    }


def _name_span(bundle, target: str, text: str):
    pred = float(bundle["nutrient_models"][target].predict([enrich(text)])[0])
    band = float(bundle["cv_cp_mae"]) if target == "cp_pct_dm" else max(1.5, abs(pred) * 0.25)
    return {
        "mean": round(pred, 2),
        "min": round(pred - band, 2),
        "max": round(pred + band, 2),
        "note": f"{bundle['best_regressor']} on the typed name; not a lab value",
    }


def assess_nutrition(ingredient: str, moisture_pct=None, form: str | None = None) -> dict:
    bundle = load_nutrition()
    lookup = bundle["lookup_df"]
    bis = bundle["bis_limits"]
    canonical = normalize_name(ingredient)
    if form == "silage" and "silage" not in canonical:
        canonical = f"{canonical} silage"
    if form == "compounded" or canonical == "compounded feed":
        return {
            "ingredient": ingredient,
            "canonical": canonical,
            "method": "bis_standard_only",
            "bis_compounded_feed": {
                "type_I_cp_min": float(bis["Crude protein"]["type_I"]),
                "type_II_cp_min": float(bis["Crude protein"]["type_II"]),
                "moisture_max": float(bis["Moisture"]["type_I"]),
                "urea_max_pct": float(bis["Urea"]["type_I"]),
                "afb1_max_ug_kg": float(bis["Aflatoxin B1"]["type_I"]),
            },
            "disclaimer": bundle["disclaimer"],
        }

    hit = lookup[lookup.canonical == canonical]
    match = "exact"
    if hit.empty:
        close = get_close_matches(canonical, bundle["canonical_names"], n=1, cutoff=0.82)
        if close:
            hit = lookup[lookup.canonical == close[0]]
            match = f"fuzzy:{close[0]}"
            canonical = close[0]

    if not hit.empty:
        row = hit.iloc[0].to_dict()
        if moisture_pct is None and pd.notna(row.get("moisture_pct_mean")):
            moisture_pct = float(row["moisture_pct_mean"])
        nutrients = {
            "crude_protein_pct_dm": _span(row, "cp_pct_dm"),
            "fibre_pct_dm": _span(row, "fibre_pct_dm"),
            "fat_ee_pct_dm": _span(row, "ee_pct_dm"),
            "energy_me_mcal_kg": _span(row, "me_mcal_kg"),
        }
        method, feed_class = "indian_table_lookup", row["feed_class"]
        sources, n_rows = row.get("sources"), int(row["n_rows"])
    else:
        feed_class = str(bundle["name_classifier"].predict([enrich(canonical)])[0])
        method, match, sources, n_rows = "best_cv_name_model", bundle["best_classifier"], None, None
        nutrients = {
            "crude_protein_pct_dm": _name_span(bundle, "cp_pct_dm", canonical),
            "fibre_pct_dm": _name_span(bundle, "fibre_pct_dm", canonical),
            "fat_ee_pct_dm": _name_span(bundle, "ee_pct_dm", canonical),
            "energy_me_mcal_kg": _name_span(bundle, "me_mcal_kg", canonical),
        }

    return {
        "ingredient": ingredient,
        "canonical": canonical,
        "moisture_pct": moisture_pct,
        "form": form,
        "method": method,
        "match": match,
        "feed_class": feed_class,
        "nutrients_pct_dm": nutrients,
        "nutrients_as_fed": {
            "crude_protein_pct": as_fed_span(nutrients.get("crude_protein_pct_dm"), moisture_pct),
            "fibre_pct": as_fed_span(nutrients.get("fibre_pct_dm"), moisture_pct),
        },
        "sources": sources,
        "n_source_rows": n_rows,
        "disclaimer": bundle["disclaimer"],
    }
