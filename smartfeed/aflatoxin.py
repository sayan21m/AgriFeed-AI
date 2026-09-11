"""AFB1 *risk* from Kotinagu 2015 incidence tables. Not a ppb predictor."""

from __future__ import annotations

import pandas as pd

from smartfeed.names import normalize_name
from smartfeed.paths import PROCESSED

BIS_AFB1_MAX_UGkg = 20.0

ALIASES = {
    "cattle feed": "Cattle feed",
    "compounded feed": "Cattle feed",
    "compounded": "Cattle feed",
    "cottonseed": "Cotton seed cake",
    "groundnut": "Groundnut cake",
    "soybean": "Soyabean cake",
    "soyabean": "Soyabean cake",
    "maize": "Maize",
    "wheat bran": "Wheat bran",
    "deoiled rice bran": "Deoiled rice bran",
    "dorb": "Deoiled rice bran",
}


def load_kotinagu() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "kotinagu_2015_afb1_ap_telangana.csv")


def _match_item(ingredient: str) -> str | None:
    text = normalize_name(ingredient)
    # Kotinagu sampled stored grain, cake and bran. Silage is a different matrix,
    # so "maize silage" must not inherit the maize-grain incidence.
    if "silage" in text:
        return None
    for key, item in ALIASES.items():
        if key in text:
            return item
    return None


def assess_aflatoxin(ingredient: str, visible_mould: bool | None = None) -> dict:
    table = load_kotinagu()
    item = _match_item(ingredient)
    row = None
    if item:
        hit = table[table["item"] == item]
        if not hit.empty:
            row = hit.iloc[0].to_dict()
    high_risk = bool(item in {"Groundnut cake", "Maize", "Cotton seed cake", "Soyabean cake"})
    if visible_mould:
        high_risk = True
    return {
        "present": True,
        "matched_item": item,
        "historical": None
        if row is None
        else {
            "n_analyzed": row["n_analyzed"],
            "incidence_pct": row["incidence_pct"],
            "mean_ppb_in_positives": row["mean_ppb"],
            "range_ppb": row["range_ppb"],
        },
        "bis_afb1_max_ug_kg": BIS_AFB1_MAX_UGkg,
        "high_risk_ingredient": high_risk,
        "visible_mould": visible_mould,
        "note": (
            "Kotinagu 2015 AP/Telangana incidence. This is not this-bag µg/kg. "
            "Need a lateral-flow strip or a lab for AFB1."
        ),
    }
