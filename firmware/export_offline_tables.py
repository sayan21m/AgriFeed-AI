#!/usr/bin/env python3
"""Bake Indian lookup + urea slopes into the Flutter JSON pack."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
LOOKUP_CSV = ROOT / "notebooks" / "ml" / "artifacts" / "ingredient_lookup.csv"
ANITHA = ROOT / "data" / "processed" / "anitha_2022_urea_foldscope_yellow_area.csv"
FLIEG = ROOT / "data" / "processed" / "flieg_score_rules.csv"
KOTINAGU = ROOT / "data" / "processed" / "kotinagu_2015_afb1_ap_telangana.csv"
BIS = ROOT / "data" / "processed" / "bis_is2052_2023_compounded_feed_limits.csv"
JSON_OUT = ROOT / "mobile" / "assets" / "offline_kit.json"


def jnum(v):
    if v is None or (isinstance(v, float) and (np.isnan(v) or pd.isna(v))):
        return None
    if isinstance(v, (np.floating, float)):
        return round(float(v), 4)
    if isinstance(v, (np.integer, int)):
        return int(v)
    return v


def main() -> None:
    df = pd.read_csv(LOOKUP_CSV)
    urea = pd.read_csv(ANITHA)
    models = {}
    for cake, sub in urea.groupby("oilseed_cake"):
        x = sub["yellow_area_pct_mean"].to_numpy(dtype=float).reshape(-1, 1)
        y = sub["urea_g_per_kg"].to_numpy(dtype=float)
        m = Ridge(alpha=0.1).fit(x, y)
        models[cake] = (float(m.intercept_), float(m.coef_[0]), float(x.min()), float(x.max()))
    gx = urea["yellow_area_pct_mean"].to_numpy(dtype=float).reshape(-1, 1)
    gy = urea["urea_g_per_kg"].to_numpy(dtype=float)
    gm = Ridge(alpha=0.1).fit(gx, gy)
    models["__global__"] = (float(gm.intercept_), float(gm.coef_[0]), float(gx.min()), float(gx.max()))
    key_map = {
        "Soyabean meal": "soybean",
        "Groundnut cake": "groundnut",
        "Un-decorticated cottonseed cake": "cotton",
        "__global__": "global",
    }

    feeds_json = []
    for rec in df.to_dict("records"):
        feeds_json.append(
            {
                "canonical": rec["canonical"],
                "feed_class": rec["feed_class"],
                "form": rec["form"],
                "n_rows": int(rec["n_rows"]),
                "sources": rec.get("sources"),
                "cp_pct_dm_mean": jnum(rec.get("cp_pct_dm_mean")),
                "cp_pct_dm_min": jnum(rec.get("cp_pct_dm_min")),
                "cp_pct_dm_max": jnum(rec.get("cp_pct_dm_max")),
                "fibre_pct_dm_mean": jnum(rec.get("fibre_pct_dm_mean")),
                "fibre_pct_dm_min": jnum(rec.get("fibre_pct_dm_min")),
                "fibre_pct_dm_max": jnum(rec.get("fibre_pct_dm_max")),
                "ee_pct_dm_mean": jnum(rec.get("ee_pct_dm_mean")),
                "ee_pct_dm_min": jnum(rec.get("ee_pct_dm_min")),
                "ee_pct_dm_max": jnum(rec.get("ee_pct_dm_max")),
                "me_mcal_kg_mean": jnum(rec.get("me_mcal_kg_mean")),
                "me_mcal_kg_min": jnum(rec.get("me_mcal_kg_min")),
                "me_mcal_kg_max": jnum(rec.get("me_mcal_kg_max")),
                "moisture_pct_mean": jnum(rec.get("moisture_pct_mean")),
            }
        )

    class_json = []
    for cls, sub in df.groupby("feed_class"):
        class_json.append(
            {
                "feed_class": cls,
                "cp_mean": jnum(sub["cp_pct_dm_mean"].mean()),
                "cp_min": jnum(sub["cp_pct_dm_min"].min()),
                "cp_max": jnum(sub["cp_pct_dm_max"].max()),
            }
        )

    urea_json = []
    for cake, (b, a, lo, hi) in models.items():
        urea_json.append(
            {
                "key": key_map[cake],
                "slope": round(a, 8),
                "intercept": round(b, 8),
                "yellow_lo": round(lo, 4),
                "yellow_hi": round(hi, 4),
                "cake_label": None if cake == "__global__" else cake,
            }
        )

    kotinagu_json = []
    for rec in pd.read_csv(KOTINAGU).to_dict("records"):
        kotinagu_json.append(
            {
                "item": rec["item"],
                "n_analyzed": jnum(rec.get("n_analyzed")),
                "incidence_pct": jnum(rec.get("incidence_pct")),
                "mean_ppb": jnum(rec.get("mean_ppb")),
                "range_ppb": None if pd.isna(rec.get("range_ppb")) else str(rec["range_ppb"]),
            }
        )

    bis_df = pd.read_csv(BIS)
    bis = {}
    name_map = {
        "Moisture": "Moisture",
        "Crude protein": "Crude protein",
        "Urea": "Urea",
        "Aflatoxin B1": "Aflatoxin B1",
        "Acid insoluble ash": "Acid insoluble ash",
    }
    for rec in bis_df.to_dict("records"):
        key = rec["characteristic"]
        if key in name_map:
            bis[key] = {"type_I": float(rec["type_I"]), "type_II": float(rec["type_II"])}

    pack = {
        "version": "1.3.0",
        "n_feeds": len(feeds_json),
        "disclaimer": (
            "Village kit on this phone: Indian table ranges + moisture + pH + 4-DMAB + "
            "HSV mould screen + AIA sand check. Unknown names use a keyword class, not ExtraTrees. "
            "NIR CP is only valid on the Brazilian forage matrix, not AS7265x. "
            "Not a lab assay of this bag."
        ),
        "feeds": feeds_json,
        "class_cp": class_json,
        "urea": urea_json,
        "flieg": pd.read_csv(FLIEG).to_dict("records"),
        "kotinagu": kotinagu_json,
        "bis": bis,
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", JSON_OUT, "feeds", len(feeds_json))


if __name__ == "__main__":
    main()
