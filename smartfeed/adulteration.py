"""Sand / silica screen against BIS acid-insoluble-ash limits.

Two honest inputs:
  * `aia_pct`      - a real acid-insoluble-ash % from a lab or union mini-kit.
  * `grit_settled_ml` + `sample_g` - the village settling-jar test (stir feed in
    water, heavy sand drops first). This is a *screen*, not an AIA assay.
"""

from __future__ import annotations

import pandas as pd

from smartfeed.paths import PROCESSED

# Millilitres of settled grit per 100 g that we treat as "clearly gritty".
GRIT_SCREEN_ML_PER_100G = 2.0


def bis_aia_limits() -> dict:
    limits = pd.read_csv(PROCESSED / "bis_is2052_2023_compounded_feed_limits.csv")
    row = limits[limits.characteristic == "Acid insoluble ash"].iloc[0]
    return {"type_I_max": float(row.type_I), "type_II_max": float(row.type_II)}


def assess_sand(
    aia_pct: float | None = None,
    grit_settled_ml: float | None = None,
    sample_g: float | None = None,
    form: str | None = None,
) -> dict:
    limits = bis_aia_limits()
    limit = limits["type_I_max"] if form == "compounded" else limits["type_II_max"]

    if aia_pct is None and grit_settled_ml is None:
        return {
            "present": False,
            "bis_aia_max_pct": limits,
            "note": "No AIA % and no settling-jar reading. Sand cannot be seen by NIR or a photo.",
        }

    out = {
        "present": True,
        "bis_aia_max_pct": limits,
        "limit_applied_pct": limit,
        "note": "AIA is the BIS test for sand/silica. The jar test only screens for it.",
    }

    if aia_pct is not None:
        out["aia_pct"] = float(aia_pct)
        out["method"] = "measured_aia"
        out["over_bis"] = float(aia_pct) > limit
        out["suspect"] = out["over_bis"]
        return out

    grit = float(grit_settled_ml)
    out["method"] = "settling_jar_screen"
    out["grit_settled_ml"] = grit
    out["over_bis"] = False  # a jar test can never prove a BIS failure
    if sample_g:
        per_100 = grit * 100.0 / float(sample_g)
        out["grit_ml_per_100g"] = round(per_100, 2)
        out["suspect"] = per_100 >= GRIT_SCREEN_ML_PER_100G
    else:
        out["suspect"] = grit > 0
        out["note"] += " Give sample_g to normalise the jar reading."
    if out["suspect"]:
        out["next_step"] = "Send a sample for acid-insoluble ash before accepting the lot."
    return out
