"""Silage Flieg score from pH + dry matter. Indian ranges are context, not this-pit lab."""

from __future__ import annotations

import pandas as pd

from smartfeed.paths import PROCESSED

FLIEG_FORMULA = "220 + (2 * DM% - 15) - 40 * pH"


def flieg_score(dm_pct: float, ph: float) -> float:
    return float(220 + (2.0 * float(dm_pct) - 15) - 40.0 * float(ph))


def _rules() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "flieg_score_rules.csv")


def classify_flieg(score: float) -> dict:
    rules = _rules()
    for rec in rules.to_dict("records"):
        if rec["min_score"] <= score <= rec["max_score"]:
            return {"class": rec["class"], "advice": rec["advice"]}
    return {"class": "unknown", "advice": "Score out of table range."}


def assess_silage(ph: float | None, moisture_pct: float | None, ingredient: str | None = None) -> dict:
    if ph is None:
        return {"present": False, "note": "Silage needs a pocket pH. Spectra and photos cannot replace it."}
    dm = None if moisture_pct is None else 100.0 - float(moisture_pct)
    out = {
        "present": True,
        "pH": float(ph),
        "dm_pct": None if dm is None else round(dm, 2),
        "formula": FLIEG_FORMULA,
        "kaur_punjab_farmer_n100": "median pH 3.99, Flieg 104 (summary, not raw pits)",
    }
    flags = []
    if float(ph) > 4.2 and (dm is None or dm < 30):
        flags.append("high_pH_low_DM")
    if dm is None:
        out["flieg"] = None
        out["note"] = "Have pH but no moisture, so Flieg is incomplete."
        out["flags"] = flags
        return out
    score = flieg_score(dm, ph)
    klass = classify_flieg(score)
    out.update({"flieg_score": round(score, 1), **klass, "flags": flags})
    if ingredient:
        out["ingredient"] = ingredient
    return out
