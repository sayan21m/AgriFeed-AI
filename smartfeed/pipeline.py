"""Fuse sensors + table models into one feed / dilute / reject advisory."""

from __future__ import annotations

from smartfeed.adulteration import assess_sand
from smartfeed.advice import farmer_card
from smartfeed.aflatoxin import assess_aflatoxin
from smartfeed.cv_mould import assess_image
from smartfeed.moisture import assess_moisture
from smartfeed.nir import assess_nir
from smartfeed.nutrition import assess_nutrition
from smartfeed.qr import verify_qr
from smartfeed.ration import ration_advice
from smartfeed.silage import assess_silage
from smartfeed.speak import spoken_advice
from smartfeed.urea import assess_urea
from smartfeed.validate import SensorRangeError, check_all

SEVERITY = {"feed": 0, "dilute": 1, "reject": 2}


def _decision(parts: dict) -> dict:
    """Collect every trigger, then take the worst. Rule order cannot change the verdict."""
    triggers: list[tuple[str, str]] = []

    urea = parts["urea"]
    if urea.get("over_bis"):
        triggers.append(("reject", "urea at or above BIS 1%"))
    elif urea.get("suspect"):
        triggers.append(("dilute", "4-DMAB yellow — suspect urea"))

    cv = parts["cv"]
    if cv.get("flag"):
        triggers.append(("reject", "visible mould"))

    silage = parts["silage"]
    if silage.get("present"):
        if silage.get("class") == "poor":
            triggers.append(("reject", f"silage Flieg {silage.get('flieg_score')} poor"))
        elif silage.get("class") == "moderate":
            triggers.append(("dilute", f"silage Flieg {silage.get('flieg_score')} moderate"))
        # Flieg can still read "satisfactory" on a pit that never acidified properly.
        if "high_pH_low_DM" in silage.get("flags", []):
            triggers.append(("dilute", f"silage pH {silage.get('pH')} above 4.2 on low DM"))

    flags = parts["moisture"].get("flags", [])
    if "above_bis_moisture_max_11" in flags:
        triggers.append(("dilute", "compounded-feed moisture above BIS 11%"))
    if "silage_too_wet_risk_effluent" in flags:
        triggers.append(("dilute", "silage too wet — effluent and clostridia risk"))

    sand = parts["sand"]
    if sand.get("over_bis"):
        triggers.append(("reject", "acid-insoluble ash above the BIS sand limit"))
    elif sand.get("suspect"):
        triggers.append(("dilute", "grit settled in the jar test — suspect sand"))

    if parts["aflatoxin"].get("high_risk_ingredient") and cv.get("flag"):
        triggers.append(("reject", "high-AF-risk ingredient plus mould"))

    qr = parts.get("qr") or {}
    if qr.get("decoded"):
        if qr.get("expired"):
            triggers.append(("dilute", "bag past expiry date (QR)"))
        if qr.get("cp_mismatch"):
            triggers.append(("dilute", "declared CP does not match tables (QR)"))
        if qr.get("moisture_mismatch"):
            triggers.append(("dilute", "declared moisture does not match measurement (QR)"))

    if not triggers:
        return {"action": "feed", "reasons": ["no reject/dilute trigger from sensors + tables"]}

    action = max((t[0] for t in triggers), key=lambda a: SEVERITY[a])
    reasons = [why for act, why in triggers if act == action]
    downgraded = [why for act, why in triggers if act != action]
    out = {"action": action, "reasons": reasons}
    if downgraded:
        out["other_flags"] = downgraded
    return out


def assess(
    ingredient: str,
    form: str | None = None,
    moisture_pct: float | None = None,
    ph: float | None = None,
    urea_yellow_area_pct: float | None = None,
    visible_mould: bool | None = None,
    image_path: str | None = None,
    nir_absorbance=None,
    aia_pct: float | None = None,
    grit_settled_ml: float | None = None,
    sample_g: float | None = None,
    qr_payload: str | None = None,
) -> dict:
    """Run every module that has an input, then decide feed / dilute / reject."""
    sensor_warnings = check_all(
        {
            "moisture_pct": moisture_pct,
            "ph": ph,
            "urea_yellow_area_pct": urea_yellow_area_pct,
            "aia_pct": aia_pct,
            "grit_settled_ml": grit_settled_ml,
            "sample_g": sample_g,
        }
    )
    nutrition = assess_nutrition(ingredient, moisture_pct=moisture_pct, form=form)
    moisture = assess_moisture(moisture_pct, form=form)
    silage = (
        assess_silage(ph, moisture_pct, ingredient)
        if form == "silage" or ph is not None
        else {"present": False, "note": "Not scored as silage."}
    )
    urea = assess_urea(urea_yellow_area_pct, ingredient)
    cv = assess_image(image_path, visible_mould)
    aflatoxin = assess_aflatoxin(ingredient, visible_mould=cv.get("flag") if cv.get("present") else visible_mould)
    nir = assess_nir(nir_absorbance)
    sand = assess_sand(aia_pct, grit_settled_ml, sample_g, form=form)
    qr = (
        verify_qr(qr_payload, nutrition)
        if qr_payload
        else {"present": False, "note": "No QR code scanned."}
    )

    parts = {
        "nutrition": nutrition,
        "moisture": moisture,
        "silage": silage,
        "urea": urea,
        "cv": cv,
        "aflatoxin": aflatoxin,
        "sand": sand,
        "nir": nir,
        "qr": qr,
    }
    decision = _decision(parts)
    farmer = farmer_card(decision)
    ration = ration_advice(nutrition)
    out = {
        "ingredient": ingredient,
        "form": form,
        "decision": decision,
        "farmer": farmer,
        "ration": ration,
        "sensor_warnings": sensor_warnings,
        "modules": parts,
        "disclaimer": (
            "Village kit: lookup + moisture + pH + 4-DMAB + mould screen + AIA sand check. "
            "NIR CP is only valid on the Brazilian forage matrix, not AS7265x."
        ),
    }
    out["spoken"] = spoken_advice(out)
    return out
