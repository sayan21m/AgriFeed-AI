#!/usr/bin/env python3
"""Tidy the Marcondes 2025 tropical-forage NIR workbook into processed CSVs."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw" / "nir" / "marcondes_2025_tropical_forage" / "Data.xlsx"
OUT = ROOT / "processed" / "nir"
CATALOG = ROOT / "processed" / "dataset_catalog.json"

SPECIES = {
    "MOM": "Megathyrsus maximus cv. Mombaça",
    "MASSAI": "Megathyrsus maximus cv. Massai",
    "MIYAGI": "Megathyrsus maximus cv. Miyagui",
    "SABIA": "Urochloa hybrid cv. Sabiá",
    "MULATOII": "Urochloa hybrid cv. Mulato II",
    "UB": "Urochloa brizantha cv. Marandu",
    "UR": "Urochloa ruziziensis",
    "UH": "Urochloa humidicola",
    "UD": "Urochloa decumbens",
    "CAPIACU": "Pennisetum purpureum cv. Capiaçu",
}

ALIAS = {
    "MYAGI": "MIYAGI",
    "MULATOII": "MULATOII",
    "MULATO2": "MULATOII",
    "CAPIACU": "CAPIACU",
}


def norm_id(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = text.upper().replace("MULATO_II", "MULATOII").replace("MULATO II", "MULATOII")
    text = re.sub(r"[^A-Z0-9]+", "_", text).strip("_")
    match = re.match(r"([A-Z]+)_?(\d+)$", text)
    if not match:
        raise ValueError(f"Cannot parse sample id: {value!r}")
    prefix = ALIAS.get(match.group(1), match.group(1))
    return f"{prefix}_{int(match.group(2))}"


def build() -> pd.DataFrame:
    if not RAW.exists():
        raise FileNotFoundError(f"Missing {RAW}. Download Data.xlsx from figshare 28734674.")

    spectra_raw = pd.read_excel(RAW, sheet_name="Spectra", header=None)
    wavelengths = [round(float(x), 3) for x in spectra_raw.iloc[0, 2:].tolist()]
    wave_cols = [f"a_{w:.3f}" for w in wavelengths]

    spectra = pd.DataFrame(
        spectra_raw.iloc[1:, 2:].to_numpy(dtype=float),
        columns=wave_cols,
    )
    spectra.insert(0, "sample_id", [norm_id(x) for x in spectra_raw.iloc[1:, 0]])
    spectra.insert(1, "species_code", spectra["sample_id"].str.split("_").str[0])
    spectra.insert(2, "species", spectra["species_code"].map(SPECIES))

    chem_raw = pd.read_excel(RAW, sheet_name="Chemical comp. and Degradation", header=None)
    chem = pd.DataFrame(
        {
            "sample_id": [norm_id(x) for x in chem_raw.iloc[2:, 0]],
            "dm_pct": pd.to_numeric(chem_raw.iloc[2:, 3], errors="coerce"),
            "om_pct": pd.to_numeric(chem_raw.iloc[2:, 4], errors="coerce"),
            "ndf_pct": pd.to_numeric(chem_raw.iloc[2:, 5], errors="coerce"),
            "adf_pct": pd.to_numeric(chem_raw.iloc[2:, 6], errors="coerce"),
            "ee_pct": pd.to_numeric(chem_raw.iloc[2:, 7], errors="coerce"),
            "cp_pct": pd.to_numeric(chem_raw.iloc[2:, 8], errors="coerce"),
            "lignin_pct": pd.to_numeric(chem_raw.iloc[2:, 11], errors="coerce"),
            "tdn_pct": pd.to_numeric(chem_raw.iloc[2:, 12], errors="coerce"),
        }
    )

    joined = spectra.merge(chem, on="sample_id", how="inner", validate="one_to_one")
    if len(joined) != 291:
        raise RuntimeError(f"Expected 291 joined rows, got {len(joined)}")

    OUT.mkdir(parents=True, exist_ok=True)
    wave_path = OUT / "marcondes_2025_wavelengths_nm.csv"
    pd.DataFrame({"wavelength_nm": wavelengths}).to_csv(wave_path, index=False)

    chem_path = OUT / "marcondes_2025_tropical_forage_chemistry.csv"
    joined[
        [
            "sample_id",
            "species_code",
            "species",
            "dm_pct",
            "om_pct",
            "ndf_pct",
            "adf_pct",
            "ee_pct",
            "cp_pct",
            "lignin_pct",
            "tdn_pct",
        ]
    ].to_csv(chem_path, index=False)

    spec_path = OUT / "marcondes_2025_tropical_forage_spectra.csv"
    spectra.to_csv(spec_path, index=False)

    joined_path = OUT / "marcondes_2025_tropical_forage_joined.csv"
    joined.to_csv(joined_path, index=False)

    catalog = json.loads(CATALOG.read_text(encoding="utf-8")) if CATALOG.exists() else []
    catalog = [row for row in catalog if "marcondes_2025" not in row.get("processed", "")]
    catalog.append(
        {
            "file": "raw/nir/marcondes_2025_tropical_forage/Data.xlsx",
            "processed": "processed/nir/marcondes_2025_tropical_forage_joined.csv",
            "type": "a_raw_downloadable",
            "use": (
                "Paired portable NIR absorbance (890–1707 nm) + wet-lab CP/NDF/ADF "
                "for 291 Brazilian tropical forages. Pipeline demo only — not Indian cattle feed."
            ),
            "citation": "https://doi.org/10.6084/m9.figshare.28734674",
            "license": "CC BY 4.0",
        }
    )
    CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    print(f"Joined rows: {len(joined)}")
    print(f"Wavelengths: {len(wavelengths)} ({wavelengths[0]:.1f}–{wavelengths[-1]:.1f} nm)")
    print(f"Wrote {joined_path}")
    return joined


if __name__ == "__main__":
    build()
