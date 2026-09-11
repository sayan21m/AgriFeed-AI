"""On-disk model pack for the farmer app.

Notebooks train. ``models/`` is what the app loads and what you replace
when a new ExtraTrees / Ridge / CNN / PLS file is ready.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

from smartfeed.paths import MODELS, ROOT

PACK_VERSION = "1.2.0"
MANIFEST = MODELS / "manifest.json"

SOURCES = (
    {
        "id": "nutrition",
        "file": "nutrition_estimator.joblib",
        "role": "ExtraTrees name class + Ridge CP",
        "src": ROOT / "notebooks" / "ml" / "artifacts" / "nutrition_estimator.joblib",
    },
    {
        "id": "nir",
        "file": "nir_forage_estimator.joblib",
        "role": "Brazilian forage PLS (not Indian bags)",
        "src": ROOT / "notebooks" / "nir" / "artifacts" / "nir_forage_estimator.joblib",
    },
    {
        "id": "mould",
        "file": "mould_vision.pt",
        "role": "CNN mould screen on 32×32 RGB",
        "src": ROOT / "notebooks" / "cv" / "artifacts" / "mould_vision.pt",
    },
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def ensure_pack() -> None:
    """Copy notebook artifacts into models/ the first time."""
    MODELS.mkdir(parents=True, exist_ok=True)
    changed = False
    for spec in SOURCES:
        dest = MODELS / spec["file"]
        if dest.exists() or not spec["src"].exists():
            continue
        shutil.copy2(spec["src"], dest)
        changed = True
    if changed or not MANIFEST.exists():
        write_manifest()


def write_manifest() -> dict:
    files = []
    for spec in SOURCES:
        dest = MODELS / spec["file"]
        if not dest.exists():
            continue
        files.append(
            {
                "id": spec["id"],
                "file": spec["file"],
                "role": spec["role"],
                "bytes": dest.stat().st_size,
                "sha256_16": _sha256(dest),
            }
        )
    payload = {
        "pack": "smartfeed-models",
        "version": PACK_VERSION,
        "updated": date.today().isoformat(),
        "note": (
            "Replace a file in models/, then tap Update in the app "
            "(POST /api/models/reload). Notebooks remain the training source."
        ),
        "files": files,
        "total_bytes": sum(f["bytes"] for f in files),
    }
    MANIFEST.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def manifest() -> dict:
    ensure_pack()
    if MANIFEST.exists():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        data["total_bytes"] = sum(int(f.get("bytes") or 0) for f in data.get("files", []))
        return data
    return write_manifest()


def pack_file(file_id: str) -> Path:
    ensure_pack()
    for spec in SOURCES:
        if spec["id"] == file_id:
            dest = MODELS / spec["file"]
            if dest.exists():
                return dest
            raise FileNotFoundError(file_id)
    raise KeyError(file_id)


def reload_runtime() -> dict:
    """Drop in-memory caches so the next assess() reads models/ again."""
    from smartfeed import cv_mould, nir, nutrition, urea

    nutrition.reload_nutrition()
    nir.reload_nir()
    cv_mould.reload_vision()
    urea.reload_urea()
    return manifest()
