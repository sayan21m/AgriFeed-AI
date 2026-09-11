"""Repo paths for SmartFeed India.

Runtime weights live in ``models/`` so the phone app can list, cache and
replace them without touching the training notebooks. Notebook artifacts
remain the training source and are used if a pack file is missing.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"
MODELS = ROOT / "models"


def _pack_or_notebook(name: str, notebook: Path) -> Path:
    packed = MODELS / name
    return packed if packed.exists() else notebook


def nutrition_joblib() -> Path:
    return _pack_or_notebook(
        "nutrition_estimator.joblib",
        ROOT / "notebooks" / "ml" / "artifacts" / "nutrition_estimator.joblib",
    )


def nir_joblib() -> Path:
    return _pack_or_notebook(
        "nir_forage_estimator.joblib",
        ROOT / "notebooks" / "nir" / "artifacts" / "nir_forage_estimator.joblib",
    )


def mould_vision() -> Path:
    return _pack_or_notebook(
        "mould_vision.pt",
        ROOT / "notebooks" / "cv" / "artifacts" / "mould_vision.pt",
    )
