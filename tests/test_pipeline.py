from pathlib import Path

import numpy as np
import pytest

from smartfeed.adulteration import assess_sand
from smartfeed.aflatoxin import assess_aflatoxin
from smartfeed.pipeline import assess
from smartfeed.silage import flieg_score
from smartfeed.urea import assess_urea
from smartfeed.validate import SensorRangeError


def test_mustard_feed():
    out = assess("mustard cake", moisture_pct=10)
    assert out["decision"]["action"] == "feed"
    assert out["modules"]["nutrition"]["method"] == "indian_table_lookup"
    assert out["farmer"]["label_hi"] == "खिलाएँ"


def test_wet_compounded_dilute():
    out = assess("cattle feed", form="compounded", moisture_pct=16)
    assert out["decision"]["action"] == "dilute"


def test_mould_reject():
    out = assess("groundnut cake", visible_mould=True)
    assert out["decision"]["action"] == "reject"


def test_flieg_formula():
    # 220 + (2*30 - 15) - 40*4.0 = 220 + 45 - 160 = 105
    assert abs(flieg_score(30, 4.0) - 105.0) < 1e-6


def test_as7265x_not_used_for_cp():
    out = assess("wheat bran", nir_absorbance=[0.1] * 18)
    assert out["modules"]["nir"]["used"] is False


def test_worst_trigger_wins_regardless_of_order():
    """A mould reject must not be softened by a milder dilute trigger."""
    out = assess("groundnut cake", visible_mould=True, moisture_pct=20, urea_yellow_area_pct=20)
    assert out["decision"]["action"] == "reject"
    assert out["decision"]["other_flags"]


def test_urea_above_calibration_is_flagged_not_extrapolated():
    r = assess_urea(95.0, "groundnut cake")
    assert r["extrapolated"] is True
    assert r["urea_pct_is_lower_bound"] is True
    assert r["over_bis"] is True
    # The curve stops at 10 g/kg, so we must not invent 15 g/kg.
    assert r["urea_g_per_kg"] <= 10.5


def test_aia_above_bis_rejects():
    out = assess("cattle feed", form="compounded", aia_pct=4.0)
    assert out["modules"]["sand"]["over_bis"] is True
    assert out["decision"]["action"] == "reject"


def test_jar_test_only_suspects_never_proves():
    r = assess_sand(grit_settled_ml=5.0, sample_g=100.0)
    assert r["suspect"] is True
    assert r["over_bis"] is False


def test_silage_does_not_inherit_maize_grain_aflatoxin_risk():
    assert assess_aflatoxin("maize silage")["matched_item"] is None
    assert assess_aflatoxin("maize")["matched_item"] == "Maize"


def test_high_ph_silage_is_not_passed_as_feed():
    out = assess("maize silage", form="silage", ph=5.2, moisture_pct=78)
    assert out["decision"]["action"] == "dilute"


def test_impossible_moisture_is_rejected():
    with pytest.raises(SensorRangeError):
        assess("mustard cake", moisture_pct=150)


def test_cnn_does_not_flag_green_silage_like_hsv():
    """HSV treats uniform green fodder as mould; the CNN was trained not to."""
    from PIL import Image

    from smartfeed.cv_mould import assess_image, mould_score
    from smartfeed.dl_mould import synthesise_batch

    rng = np.random.default_rng(0)
    x, y = synthesise_batch(40, rng)
    # kind 2 in the generator is clean green silage (label 0)
    silage = next(im for im, lab in zip(x, y) if lab == 0 and mould_score(im)["flag"])
    mould = next(im for im, lab in zip(x, y) if lab == 1)
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as sil_f:
        Image.fromarray(silage).save(sil_f.name)
        sil_path = sil_f.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as mo_f:
        Image.fromarray(mould).save(mo_f.name)
        mo_path = mo_f.name
    sil = assess_image(sil_path)
    mo = assess_image(mo_path)
    Path(sil_path).unlink(missing_ok=True)
    Path(mo_path).unlink(missing_ok=True)
    assert sil["method"].endswith("over_hsv")
    assert sil["flag"] is False
    assert mo["flag"] is True


def test_straw_tells_farmer_to_supplement():
    out = assess("wheat straw", moisture_pct=9)
    assert out["decision"]["action"] == "feed"
    assert any("below" in tip.lower() for tip in out["ration"]["tips_en"])


def test_spoken_advice_is_natural_language():
    out = assess("mustard cake", moisture_pct=10, nir_absorbance=[0.1] * 18)
    assert "mustard cake" in out["spoken"]["en"].lower()
    assert "18" in out["spoken"]["en"]
    assert "खिलाएँ" in out["spoken"]["hi"]
    assert out["modules"]["nir"]["used"] is False


def test_mineral_deficiency_advisory():
    out = assess("wheat straw", moisture_pct=9)
    assert any("ASMM" in tip for tip in out["ration"]["tips_en"])
    assert any("खनिज मिश्रण" in tip for tip in out["ration"]["tips_hi"])

    out_cake = assess("groundnut cake", moisture_pct=8)
    assert any("mineral" in tip.lower() for tip in out_cake["ration"]["tips_en"])


def test_qr_payload_verification():
    from smartfeed.qr import generate_qr_payload

    valid_payload = generate_qr_payload({
        "manufacturer": "Amul Feed Co",
        "batch_no": "B2026-09",
        "pack_date": "2026-08-01",
        "expiry_date": "2027-08-01",
        "declared_cp_pct_dm": 36.0,
        "declared_moisture_pct": 10.0,
    })
    out = assess("mustard cake", moisture_pct=10.0, qr_payload=valid_payload)
    assert out["modules"]["qr"]["verified"] is True
    assert out["decision"]["action"] == "feed"

    expired_payload = generate_qr_payload({
        "manufacturer": "Amul Feed Co",
        "expiry_date": "2020-01-01",
    })
    out_exp = assess("mustard cake", moisture_pct=10.0, qr_payload=expired_payload)
    assert out_exp["modules"]["qr"]["expired"] is True
    assert out_exp["decision"]["action"] == "dilute"
    assert any("expiry date" in r for r in out_exp["decision"]["reasons"])

    mismatch_payload = generate_qr_payload({
        "manufacturer": "Amul Feed Co",
        "declared_cp_pct_dm": 12.0,
    })
    out_mis = assess("mustard cake", moisture_pct=10.0, qr_payload=mismatch_payload)
    assert out_mis["modules"]["qr"]["cp_mismatch"] is True
    assert out_mis["decision"]["action"] == "dilute"

    raw_json = '{"manufacturer": "Amul Feed Co", "expiry_date": "2027-08-01"}'
    out_json = assess("mustard cake", moisture_pct=10.0, qr_payload=raw_json)
    assert out_json["modules"]["qr"]["decoded"] is True
    assert out_json["modules"]["qr"]["bag_info"]["manufacturer"] == "Amul Feed Co"

