#!/usr/bin/env python3
"""Verify local SmartFeed tables and re-download the public NIR workbook if missing."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
NIR_XLSX = ROOT / "raw" / "nir" / "marcondes_2025_tropical_forage" / "Data.xlsx"
NIR_URL = "https://ndownloader.figshare.com/files/53431202"
REQUIRED = [
    ROOT / "processed" / "nddb_2012_concentrate_composition.csv",
    ROOT / "processed" / "bis_is2052_2023_compounded_feed_limits.csv",
    ROOT / "processed" / "flieg_score_rules.csv",
    ROOT / "processed" / "anitha_2022_urea_foldscope_yellow_area.csv",
    ROOT / "processed" / "kotinagu_2015_afb1_ap_telangana.csv",
    ROOT / "processed" / "kaur_2026_punjab_farmer_silage_summary_n100.csv",
    ROOT / "processed" / "farmer_advisory_rules.csv",
]


def fetch_nir_xlsx() -> Path:
    NIR_XLSX.parent.mkdir(parents=True, exist_ok=True)
    if NIR_XLSX.exists() and NIR_XLSX.stat().st_size > 100_000:
        print("NIR workbook already present:", NIR_XLSX)
        return NIR_XLSX
    print("Downloading Marcondes 2025 forage NIR…")
    req = Request(NIR_URL, headers={"User-Agent": "SmartFeedIndia/1.1"})
    with urlopen(req, timeout=120) as resp, NIR_XLSX.open("wb") as out:
        out.write(resp.read())
    print("Wrote", NIR_XLSX, NIR_XLSX.stat().st_size, "bytes")
    return NIR_XLSX


def main() -> None:
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing processed tables:\n" + "\n".join(missing))
    fetch_nir_xlsx()
    catalog = json.loads((ROOT / "processed" / "dataset_catalog.json").read_text())
    print(f"Catalog entries: {len(catalog)}")
    print("All required Indian tables are on disk.")


if __name__ == "__main__":
    main()
