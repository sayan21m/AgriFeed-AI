"""SmartFeed India — SIH26111 farmer API + phone app."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.kit import latest_reading, save_reading
from smartfeed.models_store import ensure_pack, manifest as model_manifest, pack_file, reload_runtime
from smartfeed.nutrition import load_nutrition
from smartfeed.pipeline import assess
from smartfeed.validate import SensorRangeError

STATIC = Path(__file__).resolve().parent / "static"
MAX_PHOTO_BYTES = 8 * 1024 * 1024
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}

ensure_pack()

app = FastAPI(
    title="SmartFeed India",
    description="SIH26111 rapid feed and silage quality kit",
    version="1.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class KitReadingIn(BaseModel):
    device_id: str = "smartfeed-kit"
    moisture_pct: float | None = None
    ph: float | None = None
    as7265x: list[float] | None = Field(default=None, description="18 AS7265x counts, not absorbance")
    moisture_raw: int | None = None
    ph_raw: int | None = None


@app.get("/api/health")
def health():
    return {"ok": True, "problem": "SIH26111"}


@app.get("/api/ingredients")
def ingredients():
    lookup = load_nutrition()["lookup_df"]
    rows = (
        lookup[["canonical", "feed_class", "form", "cp_pct_dm_mean", "cp_pct_dm_min", "cp_pct_dm_max"]]
        .sort_values("canonical")
        .to_dict("records")
    )
    for row in rows:
        for key in ("cp_pct_dm_mean", "cp_pct_dm_min", "cp_pct_dm_max"):
            val = row.get(key)
            row[key] = None if val is None or (isinstance(val, float) and val != val) else round(float(val), 2)
    return {"n": len(rows), "items": rows}


@app.post("/api/kit")
def kit_push(body: KitReadingIn):
    """ESP32 posts moisture / pH / 18-channel colour. Photo stays on the phone."""
    try:
        return save_reading(body.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/kit")
def kit_latest():
    return {"reading": latest_reading()}


@app.post("/api/assess")
async def api_assess(
    ingredient: str = Form(...),
    form: str | None = Form(None),
    moisture_pct: float | None = Form(None),
    ph: float | None = Form(None),
    urea_yellow_area_pct: float | None = Form(None),
    visible_mould: bool | None = Form(None),
    aia_pct: float | None = Form(None),
    grit_settled_ml: float | None = Form(None),
    sample_g: float | None = Form(None),
    nir_json: str | None = Form(None),
    photo: UploadFile | None = File(None),
):
    if form in ("", "none"):
        form = None
    image_path = None
    tmp = None
    if photo is not None and photo.filename:
        if photo.content_type not in ALLOWED_PHOTO_TYPES:
            raise HTTPException(415, f"Photo must be one of {sorted(ALLOWED_PHOTO_TYPES)}.")
        blob = await photo.read(MAX_PHOTO_BYTES + 1)
        if len(blob) > MAX_PHOTO_BYTES:
            raise HTTPException(413, f"Photo is larger than {MAX_PHOTO_BYTES // (1024 * 1024)} MB.")
        suffix = Path(photo.filename).suffix or ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(blob)
        tmp.close()
        image_path = tmp.name
    spectrum = None
    if nir_json:
        try:
            spectrum = json.loads(nir_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(400, f"nir_json must be a JSON array: {exc}") from exc
    try:
        return assess(
            ingredient,
            form=form,
            moisture_pct=moisture_pct,
            ph=ph,
            urea_yellow_area_pct=urea_yellow_area_pct,
            visible_mould=visible_mould,
            image_path=image_path,
            nir_absorbance=spectrum,
            aia_pct=aia_pct,
            grit_settled_ml=grit_settled_ml,
            sample_g=sample_g,
        )
    except SensorRangeError as exc:
        raise HTTPException(400, str(exc)) from exc
    finally:
        if tmp is not None:
            Path(tmp.name).unlink(missing_ok=True)


@app.get("/api/models")
def models_status():
    """List the on-disk pack the app loads (and can replace later)."""
    return model_manifest()


@app.get("/api/models/files/{file_id}")
def models_download(file_id: str):
    try:
        path = pack_file(file_id)
    except KeyError as exc:
        raise HTTPException(404, "Unknown model id.") from exc
    except FileNotFoundError as exc:
        raise HTTPException(404, "Model file is not in models/ yet.") from exc
    return FileResponse(path, filename=path.name)


@app.post("/api/models/reload")
def models_reload():
    """After replacing files in models/, drop RAM caches so assess() rereads them."""
    return {"ok": True, "pack": reload_runtime()}


@app.get("/manifest.webmanifest")
def pwa_manifest():
    return FileResponse(STATIC / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(
        STATIC / "sw.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")

