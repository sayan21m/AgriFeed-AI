#!/usr/bin/env python3
"""Build machine-readable CSVs from legally downloaded SmartFeed India sources."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "processed"
PROCESSED.mkdir(exist_ok=True)


def write_csv(name: str, rows: list[dict], fieldnames: list[str] | None = None) -> Path:
    path = PROCESSED / name
    if not rows:
        raise ValueError(f"No rows for {name}")
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def bis_standards() -> None:
    write_csv(
        "bis_is2052_2023_compounded_feed_limits.csv",
        [
            {"characteristic": "Moisture", "unit": "% as-fed, max", "type_I": 11, "type_II": 11, "basis": "as_fed"},
            {"characteristic": "Crude protein", "unit": "% DM, min", "type_I": 22, "type_II": 20, "basis": "moisture_free"},
            {"characteristic": "Crude fat", "unit": "% DM, min", "type_I": 4.0, "type_II": 3.0, "basis": "moisture_free"},
            {"characteristic": "Crude fibre", "unit": "% DM, max", "type_I": 10, "type_II": 12, "basis": "moisture_free"},
            {"characteristic": "Acid insoluble ash", "unit": "% DM, max", "type_I": 2.5, "type_II": 3.0, "basis": "moisture_free"},
            {"characteristic": "Salt as NaCl", "unit": "% DM, max", "type_I": 1.0, "type_II": 1.0, "basis": "moisture_free"},
            {"characteristic": "Calcium", "unit": "% DM, min", "type_I": 0.8, "type_II": 0.8, "basis": "moisture_free"},
            {"characteristic": "Total phosphorus", "unit": "% DM, min", "type_I": 0.5, "type_II": 0.5, "basis": "moisture_free"},
            {"characteristic": "Available phosphorus", "unit": "% DM, min", "type_I": 0.25, "type_II": 0.25, "basis": "moisture_free"},
            {"characteristic": "Urea", "unit": "% DM, max", "type_I": 1.0, "type_II": 1.0, "basis": "moisture_free"},
            {"characteristic": "Aflatoxin B1", "unit": "ug/kg, max", "type_I": 20, "type_II": 20, "basis": "moisture_free"},
            {"characteristic": "Cadmium", "unit": "mg/kg, max", "type_I": 0.5, "type_II": 0.5, "basis": "moisture_free"},
        ],
    )
    write_csv(
        "bis_is2052_2009_annex_c_ingredient_typical_composition.csv",
        [
            {"ingredient": "Maize", "category": "grains", "moisture_pct": 10.0, "cp_pct": 9.0, "ee_pct": 4.0, "cf_pct": 2.0, "aia_pct": 0.5},
            {"ingredient": "Jowar", "category": "grains", "moisture_pct": 9.0, "cp_pct": 8.0, "ee_pct": 3.0, "cf_pct": 1.0, "aia_pct": 0.2},
            {"ingredient": "Bajra", "category": "grains", "moisture_pct": 9.0, "cp_pct": 10.0, "ee_pct": 5.0, "cf_pct": 3.0, "aia_pct": 0.4},
            {"ingredient": "Barley", "category": "grains", "moisture_pct": 10.0, "cp_pct": 9.0, "ee_pct": 2.0, "cf_pct": 4.0, "aia_pct": 0.7},
            {"ingredient": "Oat", "category": "grains", "moisture_pct": 7.0, "cp_pct": 11.0, "ee_pct": 6.0, "cf_pct": 9.0, "aia_pct": 1.0},
            {"ingredient": "Gram", "category": "grains", "moisture_pct": 9.0, "cp_pct": 22.0, "ee_pct": 3.0, "cf_pct": 10.0, "aia_pct": 1.0},
            {"ingredient": "Horse gram", "category": "grains", "moisture_pct": 9.0, "cp_pct": 25.0, "ee_pct": 1.0, "cf_pct": 6.0, "aia_pct": 0.5},
            {"ingredient": "Tuar chuni", "category": "byproducts", "moisture_pct": 7.0, "cp_pct": 20.0, "ee_pct": 3.0, "cf_pct": 18.0, "aia_pct": 0.5},
            {"ingredient": "Gram chuni", "category": "byproducts", "moisture_pct": 8.0, "cp_pct": 17.0, "ee_pct": 1.0, "cf_pct": 15.0, "aia_pct": 2.0},
            {"ingredient": "Arhar chuni", "category": "byproducts", "moisture_pct": 7.0, "cp_pct": 18.0, "ee_pct": 2.0, "cf_pct": 9.0, "aia_pct": 4.0},
            {"ingredient": "Mung chuni", "category": "byproducts", "moisture_pct": 8.0, "cp_pct": 20.0, "ee_pct": 1.0, "cf_pct": 16.0, "aia_pct": 2.0},
            {"ingredient": "Maize bran", "category": "byproducts", "moisture_pct": 8.0, "cp_pct": 11.0, "ee_pct": 2.0, "cf_pct": 9.0, "aia_pct": 0.5},
            {"ingredient": "Moth chuni", "category": "byproducts", "moisture_pct": 7.0, "cp_pct": 13.0, "ee_pct": 3.0, "cf_pct": 12.0, "aia_pct": 5.0},
            {"ingredient": "Wheat bran", "category": "byproducts", "moisture_pct": 8.0, "cp_pct": 15.0, "ee_pct": 4.0, "cf_pct": 10.0, "aia_pct": 1.0},
            {"ingredient": "Rice bran", "category": "byproducts", "moisture_pct": 9.0, "cp_pct": 13.0, "ee_pct": 16.0, "cf_pct": 12.0, "aia_pct": 5.0},
            {"ingredient": "Deoiled rice bran", "category": "byproducts", "moisture_pct": 10.0, "cp_pct": 15.0, "ee_pct": "", "cf_pct": 15.0, "aia_pct": 5.0},
            {"ingredient": "Guar meal", "category": "byproducts", "moisture_pct": 9.0, "cp_pct": 46.0, "ee_pct": 5.0, "cf_pct": 7.0, "aia_pct": 1.0},
            {"ingredient": "Gram husk", "category": "byproducts", "moisture_pct": 8.0, "cp_pct": 6.0, "ee_pct": 1.0, "cf_pct": 48.0, "aia_pct": 5.0},
            {"ingredient": "Rapeseed oil cake", "category": "oilcakes", "moisture_pct": 9.0, "cp_pct": 34.0, "ee_pct": 8.0, "cf_pct": 8.0, "aia_pct": 2.0},
            {"ingredient": "Rapeseed meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 38.0, "ee_pct": "", "cf_pct": 11.0, "aia_pct": 2.0},
            {"ingredient": "Sunflower meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 28.0, "ee_pct": "", "cf_pct": 29.0, "aia_pct": 0.6},
            {"ingredient": "Soyabean meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 45.0, "ee_pct": "", "cf_pct": 7.0, "aia_pct": 0.6},
            {"ingredient": "Cottonseed oil cake (undecorticated)", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 22.0, "ee_pct": 6.0, "cf_pct": 23.0, "aia_pct": 2.0},
            {"ingredient": "Cottonseed meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 37.0, "ee_pct": "", "cf_pct": 15.0, "aia_pct": 1.5},
            {"ingredient": "Coconut oil cake", "category": "oilcakes", "moisture_pct": 9.0, "cp_pct": 23.0, "ee_pct": 8.0, "cf_pct": 8.0, "aia_pct": 0.5},
            {"ingredient": "Coconut meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 27.0, "ee_pct": "", "cf_pct": 9.0, "aia_pct": 0.5},
            {"ingredient": "Groundnut oil cake", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 42.0, "ee_pct": 8.0, "cf_pct": 7.0, "aia_pct": 1.5},
            {"ingredient": "Groundnut meal", "category": "oilcakes", "moisture_pct": 10.0, "cp_pct": 44.0, "ee_pct": "", "cf_pct": 11.0, "aia_pct": 1.5},
            {"ingredient": "Maize cake", "category": "oilcakes", "moisture_pct": 7.0, "cp_pct": 22.0, "ee_pct": 11.0, "cf_pct": 11.0, "aia_pct": 0.5},
            {"ingredient": "Til oil cake", "category": "oilcakes", "moisture_pct": 7.0, "cp_pct": 34.0, "ee_pct": 10.0, "cf_pct": 8.0, "aia_pct": 2.0},
            {"ingredient": "Nigerseed oil cake", "category": "oilcakes", "moisture_pct": 9.0, "cp_pct": 36.0, "ee_pct": 6.0, "cf_pct": 16.0, "aia_pct": 1.0},
            {"ingredient": "Tapioca thippi", "category": "oilcakes", "moisture_pct": 6.0, "cp_pct": 3.0, "ee_pct": 0.5, "cf_pct": 11.0, "aia_pct": 4.0},
            {"ingredient": "Safflower meal", "category": "oilcakes", "moisture_pct": 6.0, "cp_pct": 20.0, "ee_pct": "", "cf_pct": 33.0, "aia_pct": 1.0},
            {"ingredient": "Linseed oil cake", "category": "oilcakes", "moisture_pct": 7.0, "cp_pct": 32.0, "ee_pct": 5.0, "cf_pct": 9.0, "aia_pct": 1.5},
            {"ingredient": "Babul chuni", "category": "waste", "moisture_pct": 8.0, "cp_pct": 16.0, "ee_pct": 4.0, "cf_pct": 13.0, "aia_pct": 2.0},
            {"ingredient": "Prosopis juliflora pods", "category": "waste", "moisture_pct": 5.0, "cp_pct": 14.0, "ee_pct": 3.0, "cf_pct": 18.0, "aia_pct": 0.5},
            {"ingredient": "Tamarind seed powder", "category": "waste", "moisture_pct": 7.0, "cp_pct": 14.0, "ee_pct": 5.0, "cf_pct": 4.0, "aia_pct": 1.0},
            {"ingredient": "Ambadi oil cake", "category": "waste", "moisture_pct": 6.0, "cp_pct": 22.0, "ee_pct": 5.0, "cf_pct": 18.0, "aia_pct": 3.0},
            {"ingredient": "Mango seed kernel", "category": "waste", "moisture_pct": 8.0, "cp_pct": 6.0, "ee_pct": 9.0, "cf_pct": 3.0, "aia_pct": 0.5},
            {"ingredient": "Cottonseed hull", "category": "waste", "moisture_pct": 8.0, "cp_pct": 7.0, "ee_pct": 2.0, "cf_pct": 42.0, "aia_pct": 0.2},
            {"ingredient": "Bijda cake", "category": "waste", "moisture_pct": 5.0, "cp_pct": 26.0, "ee_pct": 2.0, "cf_pct": 30.0, "aia_pct": 5.0},
        ],
    )


def nddb_tables() -> None:
    write_csv(
        "nddb_2012_concentrate_composition.csv",
        [
            {"ingredient": "Maize", "group": "grains", "cp_pct_dm": 9.0, "ee_pct_dm": 4.2, "cf_pct_dm": 2.0, "nfe_pct_dm": 81.6, "ash_pct_dm": 2.0, "ndf_pct_dm": 15.6, "adf_pct_dm": 3.5, "lignin_pct_dm": 1.0, "me_mcal_kg": 3.1},
            {"ingredient": "Sorghum", "group": "grains", "cp_pct_dm": 8.7, "ee_pct_dm": 2.5, "cf_pct_dm": 3.0, "nfe_pct_dm": 81.6, "ash_pct_dm": 2.8, "ndf_pct_dm": 10.9, "adf_pct_dm": 5.9, "lignin_pct_dm": 1.1, "me_mcal_kg": 3.0},
            {"ingredient": "Wheat", "group": "grains", "cp_pct_dm": 11, "ee_pct_dm": 2.6, "cf_pct_dm": 2.0, "nfe_pct_dm": 81.5, "ash_pct_dm": 2.4, "ndf_pct_dm": 16.0, "adf_pct_dm": 4.0, "lignin_pct_dm": 1.2, "me_mcal_kg": 2.9},
            {"ingredient": "Barley", "group": "grains", "cp_pct_dm": 12, "ee_pct_dm": 2.5, "cf_pct_dm": 5.9, "nfe_pct_dm": 79.0, "ash_pct_dm": 2.5, "ndf_pct_dm": 20.0, "adf_pct_dm": 7.0, "lignin_pct_dm": 2.0, "me_mcal_kg": 2.8},
            {"ingredient": "Oats", "group": "grains", "cp_pct_dm": 11, "ee_pct_dm": 4.4, "cf_pct_dm": 15.5, "nfe_pct_dm": 63.3, "ash_pct_dm": 5.0, "ndf_pct_dm": 13.8, "adf_pct_dm": 5.0, "lignin_pct_dm": 2.9, "me_mcal_kg": 2.6},
            {"ingredient": "Rice", "group": "grains", "cp_pct_dm": 9, "ee_pct_dm": 1.5, "cf_pct_dm": 10.1, "nfe_pct_dm": 72.5, "ash_pct_dm": 8.4, "ndf_pct_dm": 12.5, "adf_pct_dm": 4.3, "lignin_pct_dm": 1.5, "me_mcal_kg": 2.8},
            {"ingredient": "Bajra", "group": "grains", "cp_pct_dm": 12, "ee_pct_dm": 3.5, "cf_pct_dm": 2.0, "nfe_pct_dm": 78.4, "ash_pct_dm": 4.9, "ndf_pct_dm": 15.3, "adf_pct_dm": 5.3, "lignin_pct_dm": 2.5, "me_mcal_kg": 2.2},
            {"ingredient": "Black gram", "group": "grains", "cp_pct_dm": 29.0, "ee_pct_dm": 1.0, "cf_pct_dm": 5.3, "nfe_pct_dm": 62.1, "ash_pct_dm": 5.6, "ndf_pct_dm": 17.0, "adf_pct_dm": 2.0, "lignin_pct_dm": 7.0, "me_mcal_kg": 2.5},
            {"ingredient": "Whole cottonseed", "group": "grains", "cp_pct_dm": 22.0, "ee_pct_dm": 17.3, "cf_pct_dm": 18.0, "nfe_pct_dm": 40.0, "ash_pct_dm": 3.7, "ndf_pct_dm": 48.0, "adf_pct_dm": 42.7, "lignin_pct_dm": 17.45, "me_mcal_kg": 3.3},
            {"ingredient": "Wheat bran", "group": "milling_byproducts", "cp_pct_dm": 16.0, "ee_pct_dm": 2.2, "cf_pct_dm": 15.0, "nfe_pct_dm": 59.9, "ash_pct_dm": 8.4, "ndf_pct_dm": 64.0, "adf_pct_dm": 14.5, "lignin_pct_dm": 3.6, "me_mcal_kg": 2.7},
            {"ingredient": "Rice bran (de-oiled)", "group": "milling_byproducts", "cp_pct_dm": 17.0, "ee_pct_dm": 1.5, "cf_pct_dm": 18.0, "nfe_pct_dm": 48.1, "ash_pct_dm": 18.2, "ndf_pct_dm": 38.2, "adf_pct_dm": 11.9, "lignin_pct_dm": 4.3, "me_mcal_kg": 2.1},
            {"ingredient": "Rice polish", "group": "milling_byproducts", "cp_pct_dm": 14.0, "ee_pct_dm": 14.0, "cf_pct_dm": 12.0, "nfe_pct_dm": 49.2, "ash_pct_dm": 11.8, "ndf_pct_dm": 19.4, "adf_pct_dm": 15.0, "lignin_pct_dm": 3.0, "me_mcal_kg": 2.7},
            {"ingredient": "Brewer's grain", "group": "milling_byproducts", "cp_pct_dm": 25.4, "ee_pct_dm": 6.5, "cf_pct_dm": 14.9, "nfe_pct_dm": 48.4, "ash_pct_dm": 4.8, "ndf_pct_dm": 44.0, "adf_pct_dm": 23.0, "lignin_pct_dm": 5.5, "me_mcal_kg": 2.4},
            {"ingredient": "Cane molasses", "group": "molasses", "cp_pct_dm": 2.0, "ee_pct_dm": 8.5, "cf_pct_dm": "", "nfe_pct_dm": 84.2, "ash_pct_dm": 3.5, "ndf_pct_dm": "", "adf_pct_dm": "", "lignin_pct_dm": "", "me_mcal_kg": 2.6},
            {"ingredient": "Soybean meal", "group": "protein", "cp_pct_dm": 53.0, "ee_pct_dm": 1.4, "cf_pct_dm": 7.0, "nfe_pct_dm": 36.0, "ash_pct_dm": 8.6, "ndf_pct_dm": 18.6, "adf_pct_dm": 8.8, "lignin_pct_dm": 1.5, "me_mcal_kg": 2.5},
            {"ingredient": "Groundnut oil cake", "group": "protein", "cp_pct_dm": 40.0, "ee_pct_dm": 8.2, "cf_pct_dm": 7.4, "nfe_pct_dm": 35.9, "ash_pct_dm": 7.5, "ndf_pct_dm": 23.3, "adf_pct_dm": 18.2, "lignin_pct_dm": 3.6, "me_mcal_kg": 2.8},
            {"ingredient": "Groundnut meal", "group": "protein", "cp_pct_dm": 44.0, "ee_pct_dm": 1.0, "cf_pct_dm": 13.2, "nfe_pct_dm": 35.4, "ash_pct_dm": 6.1, "ndf_pct_dm": 31.2, "adf_pct_dm": 22.1, "lignin_pct_dm": 3.0, "me_mcal_kg": 2.7},
            {"ingredient": "Cottonseed meal (decorticated)", "group": "protein", "cp_pct_dm": 41.0, "ee_pct_dm": 9.2, "cf_pct_dm": 6.3, "nfe_pct_dm": 37.8, "ash_pct_dm": 8.2, "ndf_pct_dm": 28.0, "adf_pct_dm": 20.0, "lignin_pct_dm": 6.0, "me_mcal_kg": 2.8},
            {"ingredient": "Cottonseed meal (undecorticated)", "group": "protein", "cp_pct_dm": 22.8, "ee_pct_dm": 9.2, "cf_pct_dm": 24.1, "nfe_pct_dm": 36.6, "ash_pct_dm": 7.3, "ndf_pct_dm": 53.9, "adf_pct_dm": 41.2, "lignin_pct_dm": 11.5, "me_mcal_kg": 2.5},
            {"ingredient": "Rapeseed meal", "group": "protein", "cp_pct_dm": 42.0, "ee_pct_dm": 1.0, "cf_pct_dm": 8.5, "nfe_pct_dm": 48.2, "ash_pct_dm": 4.7, "ndf_pct_dm": 23.8, "adf_pct_dm": 15.4, "lignin_pct_dm": 2.4, "me_mcal_kg": 2.5},
            {"ingredient": "Rape seed cake", "group": "protein", "cp_pct_dm": 38.0, "ee_pct_dm": 7.5, "cf_pct_dm": 7.9, "nfe_pct_dm": 45.1, "ash_pct_dm": 4.3, "ndf_pct_dm": 25.6, "adf_pct_dm": 18.6, "lignin_pct_dm": 6.3, "me_mcal_kg": 2.9},
            {"ingredient": "Sunflower meal (undecorticated)", "group": "protein", "cp_pct_dm": 31.0, "ee_pct_dm": 6.7, "cf_pct_dm": 25.3, "nfe_pct_dm": 27.2, "ash_pct_dm": 14.0, "ndf_pct_dm": 39.9, "adf_pct_dm": 26.9, "lignin_pct_dm": 8.2, "me_mcal_kg": 1.9},
            {"ingredient": "Sesame oil cake", "group": "protein", "cp_pct_dm": 30.0, "ee_pct_dm": 10.0, "cf_pct_dm": 8.0, "nfe_pct_dm": 39.2, "ash_pct_dm": 8.6, "ndf_pct_dm": 14.3, "adf_pct_dm": 8.2, "lignin_pct_dm": 1.3, "me_mcal_kg": 2.3},
            {"ingredient": "Coconut meal", "group": "protein", "cp_pct_dm": 30.0, "ee_pct_dm": 0.5, "cf_pct_dm": 9.0, "nfe_pct_dm": 54.5, "ash_pct_dm": 9.0, "ndf_pct_dm": 37.6, "adf_pct_dm": 22.2, "lignin_pct_dm": 3.1, "me_mcal_kg": 2.3},
        ],
    )
    write_csv(
        "nddb_2012_roughage_composition.csv",
        [
            {"ingredient": "Sorghum hay", "class": "hay", "cp_pct_dm": 7.0, "ee_pct_dm": 1.2, "cf_pct_dm": 38.9, "ash_pct_dm": 8.5, "ndf_pct_dm": 56.5, "adf_pct_dm": 40.3, "me_mcal_kg": 1.9},
            {"ingredient": "Wheat hay", "class": "hay", "cp_pct_dm": 3.5, "ee_pct_dm": 1.0, "cf_pct_dm": 41.5, "ash_pct_dm": 11.0, "ndf_pct_dm": 72.3, "adf_pct_dm": 43.5, "me_mcal_kg": 1.9},
            {"ingredient": "Maize hay", "class": "hay", "cp_pct_dm": 3.6, "ee_pct_dm": 0.8, "cf_pct_dm": 33.2, "ash_pct_dm": 10.5, "ndf_pct_dm": 62.2, "adf_pct_dm": 37.4, "me_mcal_kg": 2.1},
            {"ingredient": "Oats hay", "class": "hay", "cp_pct_dm": 5.6, "ee_pct_dm": 1.7, "cf_pct_dm": 35.9, "ash_pct_dm": 8.3, "ndf_pct_dm": 58.0, "adf_pct_dm": 36.4, "me_mcal_kg": 2.0},
            {"ingredient": "Cowpea hay", "class": "hay", "cp_pct_dm": 15.0, "ee_pct_dm": 1.1, "cf_pct_dm": 34.8, "ash_pct_dm": 13.3, "ndf_pct_dm": 54.0, "adf_pct_dm": 48.0, "me_mcal_kg": 1.8},
            {"ingredient": "Lucerne hay", "class": "hay", "cp_pct_dm": 16, "ee_pct_dm": 1.4, "cf_pct_dm": 29.4, "ash_pct_dm": 12.7, "ndf_pct_dm": 43.6, "adf_pct_dm": 35.8, "me_mcal_kg": 2.0},
            {"ingredient": "Berseem hay", "class": "hay", "cp_pct_dm": 15, "ee_pct_dm": 6.6, "cf_pct_dm": 30.6, "ash_pct_dm": 12.1, "ndf_pct_dm": 49.6, "adf_pct_dm": 50.4, "me_mcal_kg": 2.4},
            {"ingredient": "Para grass hay", "class": "hay", "cp_pct_dm": 5.3, "ee_pct_dm": 2.0, "cf_pct_dm": 34.6, "ash_pct_dm": 12.3, "ndf_pct_dm": 64.4, "adf_pct_dm": 30.4, "me_mcal_kg": 1.7},
            {"ingredient": "Guinea grass hay", "class": "hay", "cp_pct_dm": 7.6, "ee_pct_dm": 1.2, "cf_pct_dm": 38.1, "ash_pct_dm": 16.0, "ndf_pct_dm": 60.5, "adf_pct_dm": 39.7, "me_mcal_kg": 1.7},
            {"ingredient": "Rhodes grass hay", "class": "hay", "cp_pct_dm": 9.4, "ee_pct_dm": 1.2, "cf_pct_dm": 36.2, "ash_pct_dm": 11.1, "ndf_pct_dm": 72.0, "adf_pct_dm": 39.8, "me_mcal_kg": 2.1},
        ],
    )


def paper_feed_tables() -> None:
    write_csv(
        "dey_2014_bihar_feed_composition.csv",
        [
            {"feed": "Paddy straw", "category": "crop_residue", "dm_pct": 88.91, "cp_pct_dm": 3.34, "cf_pct_dm": 34.40, "ee_pct_dm": 0.79, "om_pct_dm": 82.32},
            {"feed": "Wheat straw", "category": "crop_residue", "dm_pct": 91.88, "cp_pct_dm": 3.26, "cf_pct_dm": 32.27, "ee_pct_dm": 0.98, "om_pct_dm": 89.04},
            {"feed": "Maize stover", "category": "crop_residue", "dm_pct": 93.10, "cp_pct_dm": 3.24, "cf_pct_dm": 33.17, "ee_pct_dm": 0.85, "om_pct_dm": 90.86},
            {"feed": "Maize cobs", "category": "crop_residue", "dm_pct": 92.89, "cp_pct_dm": 2.94, "cf_pct_dm": 36.80, "ee_pct_dm": 0.75, "om_pct_dm": 94.17},
            {"feed": "Lentil bhusa", "category": "crop_residue", "dm_pct": 91.76, "cp_pct_dm": 8.10, "cf_pct_dm": 35.95, "ee_pct_dm": 1.24, "om_pct_dm": 83.25},
            {"feed": "Gram bhusa", "category": "crop_residue", "dm_pct": 90.60, "cp_pct_dm": 8.48, "cf_pct_dm": 39.50, "ee_pct_dm": 1.14, "om_pct_dm": 89.77},
            {"feed": "Mustard bhusa", "category": "crop_residue", "dm_pct": 92.78, "cp_pct_dm": 4.68, "cf_pct_dm": 41.50, "ee_pct_dm": 1.31, "om_pct_dm": 90.24},
            {"feed": "Mung bhusa", "category": "crop_residue", "dm_pct": 91.60, "cp_pct_dm": 10.65, "cf_pct_dm": 28.68, "ee_pct_dm": 1.55, "om_pct_dm": 86.49},
            {"feed": "Urd bhusa", "category": "crop_residue", "dm_pct": 91.78, "cp_pct_dm": 9.50, "cf_pct_dm": 27.20, "ee_pct_dm": 0.78, "om_pct_dm": 90.70},
            {"feed": "Arhar bhusa", "category": "crop_residue", "dm_pct": 90.45, "cp_pct_dm": 13.05, "cf_pct_dm": 37.88, "ee_pct_dm": 1.90, "om_pct_dm": 95.60},
            {"feed": "Wheat", "category": "grains", "dm_pct": 93.28, "cp_pct_dm": 9.34, "cf_pct_dm": 5.03, "ee_pct_dm": 2.88, "om_pct_dm": 92.25},
            {"feed": "Rice grit", "category": "grains", "dm_pct": 92.82, "cp_pct_dm": 8.38, "cf_pct_dm": 1.10, "ee_pct_dm": 1.00, "om_pct_dm": 97.95},
            {"feed": "Maize", "category": "grains", "dm_pct": 88.40, "cp_pct_dm": 9.77, "cf_pct_dm": 2.39, "ee_pct_dm": 1.75, "om_pct_dm": 94.90},
            {"feed": "Gram flour", "category": "grains", "dm_pct": 90.16, "cp_pct_dm": 18.20, "cf_pct_dm": 9.80, "ee_pct_dm": 3.50, "om_pct_dm": 88.70},
            {"feed": "Wheat bran", "category": "byproducts", "dm_pct": 89.95, "cp_pct_dm": 14.67, "cf_pct_dm": 11.21, "ee_pct_dm": 3.50, "om_pct_dm": 91.64},
            {"feed": "Rice bran", "category": "byproducts", "dm_pct": 90.38, "cp_pct_dm": 9.88, "cf_pct_dm": 23.01, "ee_pct_dm": 6.94, "om_pct_dm": 83.52},
            {"feed": "Rice polish", "category": "byproducts", "dm_pct": 90.80, "cp_pct_dm": 13.52, "cf_pct_dm": 6.65, "ee_pct_dm": 13.65, "om_pct_dm": 90.42},
            {"feed": "Deoiled rice bran", "category": "byproducts", "dm_pct": 90.20, "cp_pct_dm": 15.32, "cf_pct_dm": 17.48, "ee_pct_dm": 0.68, "om_pct_dm": 77.59},
            {"feed": "Mustard cake", "category": "oilcakes", "dm_pct": 89.88, "cp_pct_dm": 30.80, "cf_pct_dm": 9.96, "ee_pct_dm": 8.33, "om_pct_dm": 84.14},
            {"feed": "Linseed cake", "category": "oilcakes", "dm_pct": 90.22, "cp_pct_dm": 32.68, "cf_pct_dm": 8.65, "ee_pct_dm": 3.32, "om_pct_dm": 91.50},
            {"feed": "Til cake", "category": "oilcakes", "dm_pct": 91.30, "cp_pct_dm": 31.56, "cf_pct_dm": 6.70, "ee_pct_dm": 5.50, "om_pct_dm": 82.06},
            {"feed": "Sugarcane tops", "category": "other", "dm_pct": 37.43, "cp_pct_dm": 5.04, "cf_pct_dm": 32.98, "ee_pct_dm": 2.70, "om_pct_dm": 92.40},
            {"feed": "Local grass", "category": "other", "dm_pct": 34.50, "cp_pct_dm": 8.46, "cf_pct_dm": 27.43, "ee_pct_dm": 1.70, "om_pct_dm": 87.90},
        ],
    )
    write_csv(
        "singh_2016_indian_energy_protein_feeds.csv",
        [
            {"feed": "Barley grain", "class": "Energy", "cp_g_kg_dm": 103, "om_g_kg_dm": 943, "ee_g_kg_dm": 15.2, "ndf_g_kg_dm": 414, "adf_g_kg_dm": 157, "cellulose_g_kg_dm": 113, "lignin_g_kg_dm": 23.0},
            {"feed": "Chickpea husk", "class": "Energy", "cp_g_kg_dm": 45.0, "om_g_kg_dm": 951, "ee_g_kg_dm": 5.88, "ndf_g_kg_dm": 672, "adf_g_kg_dm": 648, "cellulose_g_kg_dm": 592, "lignin_g_kg_dm": 55.5},
            {"feed": "Maize grain", "class": "Energy", "cp_g_kg_dm": 99.1, "om_g_kg_dm": 979, "ee_g_kg_dm": 47.7, "ndf_g_kg_dm": 364, "adf_g_kg_dm": 61.8, "cellulose_g_kg_dm": 47.6, "lignin_g_kg_dm": 15.5},
            {"feed": "Oat grain", "class": "Energy", "cp_g_kg_dm": 96.4, "om_g_kg_dm": 963, "ee_g_kg_dm": 52.3, "ndf_g_kg_dm": 351, "adf_g_kg_dm": 156, "cellulose_g_kg_dm": 134, "lignin_g_kg_dm": 12.5},
            {"feed": "Rice bran", "class": "Energy", "cp_g_kg_dm": 70.1, "om_g_kg_dm": 803, "ee_g_kg_dm": 45.6, "ndf_g_kg_dm": 668, "adf_g_kg_dm": 523, "cellulose_g_kg_dm": 249, "lignin_g_kg_dm": 128},
            {"feed": "Wheat bran A", "class": "Energy", "cp_g_kg_dm": 132, "om_g_kg_dm": 929, "ee_g_kg_dm": 27.1, "ndf_g_kg_dm": 560, "adf_g_kg_dm": 174, "cellulose_g_kg_dm": 121, "lignin_g_kg_dm": 39.8},
            {"feed": "Wheat bran B", "class": "Energy", "cp_g_kg_dm": 154, "om_g_kg_dm": 940, "ee_g_kg_dm": 34.9, "ndf_g_kg_dm": 399, "adf_g_kg_dm": 121, "cellulose_g_kg_dm": 86.0, "lignin_g_kg_dm": 31.4},
            {"feed": "Wheat grain", "class": "Energy", "cp_g_kg_dm": 117, "om_g_kg_dm": 973, "ee_g_kg_dm": 14.2, "ndf_g_kg_dm": 319, "adf_g_kg_dm": 43.6, "cellulose_g_kg_dm": 30.8, "lignin_g_kg_dm": 7.55},
            {"feed": "Coconut cake", "class": "Protein", "cp_g_kg_dm": 254, "om_g_kg_dm": 937, "ee_g_kg_dm": 61.3, "ndf_g_kg_dm": 596, "adf_g_kg_dm": 228, "cellulose_g_kg_dm": 195, "lignin_g_kg_dm": 38.9},
            {"feed": "Cotton seed cake", "class": "Protein", "cp_g_kg_dm": 240, "om_g_kg_dm": 951, "ee_g_kg_dm": 72.0, "ndf_g_kg_dm": 517, "adf_g_kg_dm": 365, "cellulose_g_kg_dm": 261, "lignin_g_kg_dm": 100},
            {"feed": "Groundnut cake", "class": "Protein", "cp_g_kg_dm": 332, "om_g_kg_dm": 924, "ee_g_kg_dm": 106, "ndf_g_kg_dm": 322, "adf_g_kg_dm": 247, "cellulose_g_kg_dm": 152, "lignin_g_kg_dm": 81.6},
            {"feed": "Mustard seed cake", "class": "Protein", "cp_g_kg_dm": 348, "om_g_kg_dm": 895, "ee_g_kg_dm": 82.0, "ndf_g_kg_dm": 264, "adf_g_kg_dm": 223, "cellulose_g_kg_dm": 123, "lignin_g_kg_dm": 72.2},
        ],
    )
    write_csv(
        "kannan_2017_nw_himalayan_concentrates.csv",
        [
            {"feed": "Maize", "class": "Energy", "om_pct_dm": 97.86, "cp_pct_dm": 9.29, "ee_pct_dm": 4.07, "ndf_pct_dm": 18.19, "adf_pct_dm": 5.25, "lignin_pct_dm": 1.33},
            {"feed": "Wheat", "class": "Energy", "om_pct_dm": 97.81, "cp_pct_dm": 11.14, "ee_pct_dm": 2.17, "ndf_pct_dm": 21.48, "adf_pct_dm": 6.10, "lignin_pct_dm": 1.53},
            {"feed": "Jowar", "class": "Energy", "om_pct_dm": 97.37, "cp_pct_dm": 8.81, "ee_pct_dm": 2.72, "ndf_pct_dm": 18.42, "adf_pct_dm": 6.33, "lignin_pct_dm": 1.53},
            {"feed": "Broken rice", "class": "Energy", "om_pct_dm": 98.90, "cp_pct_dm": 8.80, "ee_pct_dm": 1.98, "ndf_pct_dm": 23.20, "adf_pct_dm": 11.14, "lignin_pct_dm": 0.98},
            {"feed": "Wheat bran", "class": "Energy", "om_pct_dm": 94.19, "cp_pct_dm": 15.29, "ee_pct_dm": 3.24, "ndf_pct_dm": 53.14, "adf_pct_dm": 14.54, "lignin_pct_dm": 3.16},
            {"feed": "Deoiled rice bran", "class": "Energy", "om_pct_dm": 87.26, "cp_pct_dm": 14.84, "ee_pct_dm": 0.65, "ndf_pct_dm": 50.65, "adf_pct_dm": 21.60, "lignin_pct_dm": 5.77},
            {"feed": "Rice polish", "class": "Energy", "om_pct_dm": 87.11, "cp_pct_dm": 13.11, "ee_pct_dm": 13.76, "ndf_pct_dm": 39.40, "adf_pct_dm": 21.67, "lignin_pct_dm": 6.94},
            {"feed": "Groundnut meal", "class": "Protein", "om_pct_dm": 93.30, "cp_pct_dm": 42.67, "ee_pct_dm": 1.00, "ndf_pct_dm": 15.71, "adf_pct_dm": 7.50, "lignin_pct_dm": 3.43},
            {"feed": "Mustard cake", "class": "Protein", "om_pct_dm": 94.55, "cp_pct_dm": 37.10, "ee_pct_dm": 7.88, "ndf_pct_dm": 24.52, "adf_pct_dm": 15.73, "lignin_pct_dm": 3.33},
            {"feed": "Deoiled mustard cake", "class": "Protein", "om_pct_dm": 91.67, "cp_pct_dm": 37.31, "ee_pct_dm": 0.83, "ndf_pct_dm": 38.75, "adf_pct_dm": 20.82, "lignin_pct_dm": 3.22},
            {"feed": "Soybean meal", "class": "Protein", "om_pct_dm": 91.05, "cp_pct_dm": 45.23, "ee_pct_dm": 1.12, "ndf_pct_dm": 21.50, "adf_pct_dm": 11.91, "lignin_pct_dm": 1.75},
            {"feed": "Groundnut cake", "class": "Protein", "om_pct_dm": 93.86, "cp_pct_dm": 42.11, "ee_pct_dm": 7.95, "ndf_pct_dm": 25.20, "adf_pct_dm": 17.57, "lignin_pct_dm": 3.41},
        ],
    )


def silage_tables() -> None:
    write_csv(
        "kaur_2026_punjab_farmer_silage_summary_n100.csv",
        [
            {"parameter": "DM", "unit": "%", "n": 100, "mean": 29.52, "sd": 1.30, "min": 26.25, "q1": 28.65, "median": 29.48, "q3": 30.35, "max": 32.65},
            {"parameter": "pH", "unit": "pH", "n": 100, "mean": 4.34, "sd": 0.93, "min": 3.10, "q1": 3.61, "median": 3.99, "q3": 4.90, "max": 7.47},
            {"parameter": "CP", "unit": "%", "n": 100, "mean": 9.36, "sd": 0.88, "min": 6.57, "q1": 8.69, "median": 9.36, "q3": 9.88, "max": 11.37},
            {"parameter": "Lactic acid", "unit": "%", "n": 100, "mean": 4.34, "sd": 0.58, "min": 2.83, "q1": 4.04, "median": 4.30, "q3": 4.61, "max": 6.52},
            {"parameter": "NH3N", "unit": "%", "n": 100, "mean": 9.82, "sd": 2.30, "min": 5.12, "q1": 7.96, "median": 9.67, "q3": 11.79, "max": 14.70},
            {"parameter": "Fleig Point", "unit": "score", "n": 100, "mean": 90.58, "sd": 36.82, "min": -34.10, "q1": 68.40, "median": 104.10, "q3": 116.80, "max": 142.80},
        ],
    )
    write_csv(
        "brar_2021_punjab_maize_cultivar_silage.csv",
        [
            {"cultivar": "J 1006", "pH": 4.38, "lactic_acid_pct_dm": 6.50, "ammonia_n_pct_total_n": 2.30, "dm_pct": 21.90, "cp_pct_dm": 5.55, "ee_pct_dm": 1.77, "ndf_pct_dm": 73.60, "adf_pct_dm": 36.90, "ash_pct_dm": 5.20, "tdn_pct": 62.01},
            {"cultivar": "PMH 10", "pH": 4.10, "lactic_acid_pct_dm": 8.30, "ammonia_n_pct_total_n": 1.97, "dm_pct": 19.53, "cp_pct_dm": 8.44, "ee_pct_dm": 2.07, "ndf_pct_dm": 66.40, "adf_pct_dm": 35.77, "ash_pct_dm": 6.70, "tdn_pct": 62.82},
            {"cultivar": "DKC 9108", "pH": 4.29, "lactic_acid_pct_dm": 7.17, "ammonia_n_pct_total_n": 1.97, "dm_pct": 22.47, "cp_pct_dm": 8.15, "ee_pct_dm": 2.07, "ndf_pct_dm": 65.50, "adf_pct_dm": 35.97, "ash_pct_dm": 7.50, "tdn_pct": 62.68},
        ],
    )
    write_csv(
        "hundal_2020_wheat_silage.csv",
        [
            {"cultivar": "PBW 343", "stage": "Head", "cp_pct_dm": 8.06, "ee_pct_dm": 2.15, "ndf_pct_dm": 68.6, "adf_pct_dm": 42.9, "ash_pct_dm": 7.80, "tdn_pct": 57.8, "flieg_score": 100.7, "pH": 4.15, "lactic_acid_pct_dm": 6.44, "acetic_acid_pct_dm": 1.84, "ammonia_n_pct_tn": 3.88},
            {"cultivar": "PBW 343", "stage": "Milk", "cp_pct_dm": 7.72, "ee_pct_dm": 2.15, "ndf_pct_dm": 64.6, "adf_pct_dm": 40.3, "ash_pct_dm": 9.04, "tdn_pct": 59.6, "flieg_score": 87.0, "pH": 4.42, "lactic_acid_pct_dm": 6.28, "acetic_acid_pct_dm": 1.73, "ammonia_n_pct_tn": 5.51},
            {"cultivar": "HD 3086", "stage": "Head", "cp_pct_dm": 8.51, "ee_pct_dm": 1.90, "ndf_pct_dm": 64.5, "adf_pct_dm": 36.3, "ash_pct_dm": 7.7, "tdn_pct": 62.4, "flieg_score": 105.2, "pH": 4.25, "lactic_acid_pct_dm": 6.26, "acetic_acid_pct_dm": 1.16, "ammonia_n_pct_tn": 2.31},
            {"cultivar": "HD 3086", "stage": "Milk", "cp_pct_dm": 7.25, "ee_pct_dm": 2.15, "ndf_pct_dm": 62.9, "adf_pct_dm": 36.2, "ash_pct_dm": 8.00, "tdn_pct": 62.5, "flieg_score": 52.9, "pH": 4.41, "lactic_acid_pct_dm": 6.04, "acetic_acid_pct_dm": 1.20, "ammonia_n_pct_tn": 2.84},
            {"cultivar": "HD 2967", "stage": "Head", "cp_pct_dm": 8.80, "ee_pct_dm": 2.25, "ndf_pct_dm": 64.2, "adf_pct_dm": 35.95, "ash_pct_dm": 7.4, "tdn_pct": 62.67, "flieg_score": 90.1, "pH": 4.38, "lactic_acid_pct_dm": 6.09, "acetic_acid_pct_dm": 1.08, "ammonia_n_pct_tn": 2.34},
            {"cultivar": "HD 2967", "stage": "Milk", "cp_pct_dm": 7.12, "ee_pct_dm": 2.20, "ndf_pct_dm": 62.6, "adf_pct_dm": 35.90, "ash_pct_dm": 7.5, "tdn_pct": 62.7, "flieg_score": 52.8, "pH": 4.41, "lactic_acid_pct_dm": 5.13, "acetic_acid_pct_dm": 1.18, "ammonia_n_pct_tn": 3.16},
            {"cultivar": "PBW 725", "stage": "Head", "cp_pct_dm": 9.70, "ee_pct_dm": 2.25, "ndf_pct_dm": 63.8, "adf_pct_dm": 34.5, "ash_pct_dm": 7.35, "tdn_pct": 63.7, "flieg_score": 105.6, "pH": 4.24, "lactic_acid_pct_dm": 6.01, "acetic_acid_pct_dm": 1.51, "ammonia_n_pct_tn": 2.51},
            {"cultivar": "PBW 725", "stage": "Milk", "cp_pct_dm": 8.33, "ee_pct_dm": 2.00, "ndf_pct_dm": 61.2, "adf_pct_dm": 34.6, "ash_pct_dm": 7.25, "tdn_pct": 63.6, "flieg_score": 103.0, "pH": 4.27, "lactic_acid_pct_dm": 5.70, "acetic_acid_pct_dm": 1.59, "ammonia_n_pct_tn": 4.58},
        ],
    )
    write_csv(
        "flieg_score_rules.csv",
        [
            {"min_score": 81, "max_score": 1000, "class": "very_good", "advice": "Good fermentation. Feed normally and keep silo face clean."},
            {"min_score": 61, "max_score": 80, "class": "good", "advice": "Acceptable quality. Use soon and avoid heating at the face."},
            {"min_score": 41, "max_score": 60, "class": "satisfactory", "advice": "Fair quality. Mix with better forage if animals refuse."},
            {"min_score": 21, "max_score": 40, "class": "moderate", "advice": "Poor fermentation. Limit feeding and check for mould."},
            {"min_score": -1000, "max_score": 20, "class": "poor", "advice": "Reject or get a lab test. High pH or low DM risk."},
        ],
    )


def contamination_tables() -> None:
    write_csv(
        "kotinagu_2015_afb1_ap_telangana.csv",
        [
            {"item": "Cattle feed", "group": "compound", "n_analyzed": 24, "n_positive": 6, "incidence_pct": 26, "mean_ppb": 32, "range_ppb": "20-60"},
            {"item": "Poultry feed", "group": "compound", "n_analyzed": 17, "n_positive": 6, "incidence_pct": 35.2, "mean_ppb": 13.4, "range_ppb": "10-20"},
            {"item": "Cotton seed cake", "group": "ingredient", "n_analyzed": 7, "n_positive": 3, "incidence_pct": 42.8, "mean_ppb": 23.3, "range_ppb": "10-40"},
            {"item": "Groundnut cake", "group": "ingredient", "n_analyzed": 5, "n_positive": 3, "incidence_pct": 60, "mean_ppb": 23.3, "range_ppb": "20-30"},
            {"item": "Soyabean cake", "group": "ingredient", "n_analyzed": 3, "n_positive": 1, "incidence_pct": 33.3, "mean_ppb": 50, "range_ppb": ""},
            {"item": "Maize", "group": "ingredient", "n_analyzed": 13, "n_positive": 5, "incidence_pct": 38.4, "mean_ppb": 62, "range_ppb": ""},
            {"item": "Wheat bran", "group": "ingredient", "n_analyzed": 2, "n_positive": 0, "incidence_pct": 0, "mean_ppb": "", "range_ppb": ""},
            {"item": "Deoiled rice bran", "group": "ingredient", "n_analyzed": 4, "n_positive": 0, "incidence_pct": 0, "mean_ppb": "", "range_ppb": ""},
        ],
    )
    write_csv(
        "anitha_2022_urea_foldscope_yellow_area.csv",
        [
            {"oilseed_cake": "Soyabean meal", "urea_g_per_kg": 1, "yellow_area_pct_mean": 6.66, "yellow_area_pct_se": 0.48},
            {"oilseed_cake": "Soyabean meal", "urea_g_per_kg": 5, "yellow_area_pct_mean": 29.99, "yellow_area_pct_se": 0.94},
            {"oilseed_cake": "Soyabean meal", "urea_g_per_kg": 10, "yellow_area_pct_mean": 59.58, "yellow_area_pct_se": 0.64},
            {"oilseed_cake": "Groundnut cake", "urea_g_per_kg": 1, "yellow_area_pct_mean": 7.35, "yellow_area_pct_se": 0.50},
            {"oilseed_cake": "Groundnut cake", "urea_g_per_kg": 5, "yellow_area_pct_mean": 32.35, "yellow_area_pct_se": 0.95},
            {"oilseed_cake": "Groundnut cake", "urea_g_per_kg": 10, "yellow_area_pct_mean": 63.60, "yellow_area_pct_se": 0.98},
            {"oilseed_cake": "Un-decorticated cottonseed cake", "urea_g_per_kg": 1, "yellow_area_pct_mean": 8.19, "yellow_area_pct_se": 0.84},
            {"oilseed_cake": "Un-decorticated cottonseed cake", "urea_g_per_kg": 5, "yellow_area_pct_mean": 34.0, "yellow_area_pct_se": 0.79},
            {"oilseed_cake": "Un-decorticated cottonseed cake", "urea_g_per_kg": 10, "yellow_area_pct_mean": 67.35, "yellow_area_pct_se": 0.89},
        ],
    )


def advisory_and_catalog() -> None:
    write_csv(
        "farmer_advisory_rules.csv",
        [
            {"rule_id": "SILAGE_PH_DM", "module": "silage", "condition": "compute Flieg = 220 + (2*DM_pct - 15) - 40*pH", "action": "Use flieg_score_rules.csv class"},
            {"rule_id": "SILAGE_HIGH_PH", "module": "silage", "condition": "pH > 4.2 and DM_pct < 30", "action": "Flag poor fermentation even before Flieg"},
            {"rule_id": "FEED_LOOKUP", "module": "nutrient", "condition": "farmer selects ingredient", "action": "Return NDDB/BIS/Dey typical CP, CF, EE, ash, TDN/ME"},
            {"rule_id": "COMPOUND_BIS", "module": "nutrient", "condition": "sample is compounded cattle feed", "action": "Compare moisture, CP, fat, CF, AIA against IS 2052:2023 Type I/II"},
            {"rule_id": "UREA_DMAB", "module": "adulteration", "condition": "4-DMAB yellow on oilcake", "action": "Suspect urea; BIS max 1% if urea is declared"},
            {"rule_id": "AIA_SAND", "module": "adulteration", "condition": "AIA above 2.5% (Type I) or 3.0% (Type II)", "action": "Possible sand/silica contamination"},
            {"rule_id": "MOULD_MOISTURE", "module": "mould", "condition": "visible mould or moisture high in store", "action": "Do not claim ppb; advise reject or lab AFB1 test"},
            {"rule_id": "AFB1_RISK", "module": "mycotoxin", "condition": "maize or groundnut cake, monsoon, poor storage", "action": "High-risk ingredient; BIS AFB1 max 20 ug/kg"},
        ],
    )
    catalog = [
        {
            "file": "raw/nddb/NDDB_Nutritive_Value_Feeds_Fodders_India_2012.pdf",
            "processed": "processed/nddb_2012_concentrate_composition.csv",
            "type": "c_reference_tables",
            "use": "Primary feed-nutrient lookup",
        },
        {
            "file": "raw/nddb/NDDB_Nutritive_Value_Feeds_Fodders_India_2012.pdf",
            "processed": "processed/nddb_2012_roughage_composition.csv",
            "type": "c_reference_tables",
            "use": "Roughage lookup (straw, stover, silage, green fodder)",
        },
        {
            "file": "raw/bis/IS_2052_2023_Compounded_Feeds_for_Cattle.pdf",
            "processed": "processed/bis_is2052_2023_compounded_feed_limits.csv",
            "type": "c_standard",
            "use": "Pass/fail limits for compounded feed, urea, AIA, AFB1",
        },
        {
            "file": "raw/bis/IS_2052_2009_Compounded_Cattle_Feeds.pdf",
            "processed": "processed/bis_is2052_2009_annex_c_ingredient_typical_composition.csv",
            "type": "c_standard",
            "use": "Typical ingredient composition including AIA",
        },
        {
            "file": "raw/icar_papers/Dey_2014_IJAnS_Bihar_feed_composition.pdf",
            "processed": "processed/dey_2014_bihar_feed_composition.csv",
            "type": "b_paper_table",
            "use": "Extra Indian concentrate/roughage composition rows",
        },
        {
            "file": "raw/icar_papers/Singh_2016_IJAnS_energy_protein_feeds.pdf",
            "processed": "processed/singh_2016_indian_energy_protein_feeds.csv",
            "type": "b_paper_table",
            "use": "Extra Indian energy and protein feed rows",
        },
        {
            "file": "raw/icar_papers/Kannan_2017_IJAnS_NW_Himalayan_concentrates.pdf",
            "processed": "processed/kannan_2017_nw_himalayan_concentrates.csv",
            "type": "b_paper_table",
            "use": "NW Himalayan concentrate composition",
        },
        {
            "file": "raw/icar_papers/Kaur_2026_IJDS_Punjab_farmer_silage.pdf",
            "processed": "processed/kaur_2026_punjab_farmer_silage_summary_n100.csv",
            "type": "b_paper_table",
            "use": "Silage quality ranges and Flieg calibration (n=100 summary, not raw rows)",
        },
        {
            "file": "raw/icar_papers/Hundal_2020_IJAnS_wheat_silage.pdf",
            "processed": "processed/hundal_2020_wheat_silage.csv",
            "type": "b_paper_table",
            "use": "Experimental silage pH, acids, Flieg, TDN",
        },
        {
            "file": "raw/icar_papers/Brar_2021_IJAgS_maize_cultivar_silage.pdf",
            "processed": "processed/brar_2021_punjab_maize_cultivar_silage.csv",
            "type": "b_paper_table",
            "use": "Maize silage fermentation and nutrient demo rows",
        },
        {
            "file": "raw/urea/Anitha_2022_ARCC_urea_foldscope_oilseed_cakes.pdf",
            "processed": "processed/anitha_2022_urea_foldscope_yellow_area.csv",
            "type": "b_paper_table",
            "use": "Urea screening method thresholds",
        },
        {
            "file": "raw/aflatoxin/Kotinagu_2015_VeterinaryWorld_AFB1.pdf",
            "processed": "processed/kotinagu_2015_afb1_ap_telangana.csv",
            "type": "b_paper_table",
            "use": "AFB1 risk advisory, not ppb prediction",
        },
        {
            "file": null,
            "processed": "processed/flieg_score_rules.csv",
            "type": "derived_rules",
            "use": "Flieg class cut-points used by silage scoring",
        },
        {
            "file": null,
            "processed": "processed/farmer_advisory_rules.csv",
            "type": "derived_rules",
            "use": "Fused village-kit decision rules",
        },
    ]
    (PROCESSED / "dataset_catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")


def main() -> None:
    bis_standards()
    nddb_tables()
    paper_feed_tables()
    silage_tables()
    contamination_tables()
    advisory_and_catalog()
    files = sorted(PROCESSED.glob("*"))
    print(f"Wrote {len(files)} files to {PROCESSED}")
    for path in files:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()
