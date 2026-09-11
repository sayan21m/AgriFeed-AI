import io

import pytest
from fastapi.testclient import TestClient

from app.main import MAX_PHOTO_BYTES, app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"ok": True, "problem": "SIH26111"}


def test_ingredients_listed():
    data = client.get("/api/ingredients").json()
    assert data["n"] == 77
    assert all("canonical" in row for row in data["items"])


def test_assess_returns_farmer_card_and_ration():
    res = client.post("/api/assess", data={"ingredient": "mustard cake", "moisture_pct": 10})
    assert res.status_code == 200
    body = res.json()
    assert body["decision"]["action"] == "feed"
    assert body["farmer"]["label_hi"] == "खिलाएँ"
    assert body["ration"]["tips_en"]


def test_assess_rejects_impossible_moisture():
    res = client.post("/api/assess", data={"ingredient": "mustard cake", "moisture_pct": 150})
    assert res.status_code == 400
    assert "moisture_pct" in res.json()["detail"]


def test_assess_rejects_bad_nir_json():
    res = client.post("/api/assess", data={"ingredient": "wheat bran", "nir_json": "not-json"})
    assert res.status_code == 400


def test_photo_type_is_enforced():
    files = {"photo": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    res = client.post("/api/assess", data={"ingredient": "maize"}, files=files)
    assert res.status_code == 415


def test_oversized_photo_is_rejected():
    blob = io.BytesIO(b"\x00" * (MAX_PHOTO_BYTES + 10))
    files = {"photo": ("big.jpg", blob, "image/jpeg")}
    res = client.post("/api/assess", data={"ingredient": "maize"}, files=files)
    assert res.status_code == 413


def test_sand_inputs_reach_the_pipeline():
    res = client.post(
        "/api/assess",
        data={"ingredient": "cattle feed", "form": "compounded", "aia_pct": 4.0},
    )
    assert res.json()["decision"]["action"] == "reject"


def test_index_and_static_served():
    html = client.get("/").text
    assert "tabbar" in html
    assert "screen-models" in html
    for asset in ("/static/styles.css", "/static/app.js", "/manifest.webmanifest", "/sw.js"):
        assert client.get(asset).status_code == 200


def test_model_pack_is_listed_and_reloadable():
    pack = client.get("/api/models").json()
    assert pack["pack"] == "smartfeed-models"
    ids = {row["id"] for row in pack["files"]}
    assert {"nutrition", "nir", "mould"} <= ids
    blob = client.get("/api/models/files/nutrition")
    assert blob.status_code == 200
    assert len(blob.content) > 1000
    reloaded = client.post("/api/models/reload").json()
    assert reloaded["ok"] is True
    assert client.post("/api/assess", data={"ingredient": "mustard cake", "moisture_pct": 10}).status_code == 200


def test_unknown_model_file_is_404():
    assert client.get("/api/models/files/not-a-model").status_code == 404


def test_kit_accepts_esp32_payload():
    res = client.post(
        "/api/kit",
        json={
            "device_id": "kit-01",
            "moisture_pct": 10.4,
            "ph": 3.9,
            "as7265x": [0.1] * 18,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["device_id"] == "kit-01"
    assert body["as7265x_channels_nm"][0] == 410
    latest = client.get("/api/kit").json()["reading"]
    assert latest["moisture_pct"] == 10.4


def test_kit_rejects_wrong_band_count():
    res = client.post("/api/kit", json={"as7265x": [0.1] * 6})
    assert res.status_code == 400


def test_assess_returns_spoken_paragraph():
    res = client.post("/api/assess", data={"ingredient": "mustard cake", "moisture_pct": 10})
    spoken = res.json()["spoken"]
    assert "mustard cake" in spoken["en"].lower()
    assert spoken["hi"]


def test_assess_with_qr_payload():
    from smartfeed.qr import generate_qr_payload

    payload = generate_qr_payload({
        "manufacturer": "Amul Feed",
        "batch_no": "B101",
        "declared_cp_pct_dm": 36.0,
    })
    res = client.post(
        "/api/assess",
        data={"ingredient": "mustard cake", "moisture_pct": 10, "qr_payload": payload},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["modules"]["qr"]["present"] is True
    assert body["modules"]["qr"]["verified"] is True
    assert body["modules"]["qr"]["bag_info"]["manufacturer"] == "Amul Feed"

