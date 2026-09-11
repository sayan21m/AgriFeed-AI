"""Turn an assess() result into a short spoken paragraph the farmer can hear."""

from __future__ import annotations


def _cp_span(nutrition: dict) -> dict | None:
    return (nutrition.get("nutrients_pct_dm") or {}).get("crude_protein_pct_dm")


def _asfed_span(nutrition: dict) -> dict | None:
    return (nutrition.get("nutrients_as_fed") or {}).get("crude_protein_pct")


def spoken_advice(result: dict) -> dict:
    farmer = result.get("farmer") or {}
    nutrition = (result.get("modules") or {}).get("nutrition") or {}
    moisture = (result.get("modules") or {}).get("moisture") or {}
    silage = (result.get("modules") or {}).get("silage") or {}
    nir = (result.get("modules") or {}).get("nir") or {}
    cv = (result.get("modules") or {}).get("cv") or {}
    ration = result.get("ration") or {}
    name = result.get("ingredient") or nutrition.get("canonical") or "this feed"
    action = farmer.get("action", "feed")

    return {
        "en": _english(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result),
        "hi": _hindi(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result),
    }


def _english(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result) -> str:
    parts = [f"{farmer.get('label_en', 'Feed')}. {farmer.get('summary_en', '')}".strip()]
    parts.append(f"You tested {name}.")

    span = _cp_span(nutrition)
    if span and span.get("min") is not None:
        parts.append(
            f"Indian tables put crude protein around {span['min']}–{span['max']}% on dry matter"
            f" (about {span['mean']}% typical)."
        )
    elif nutrition.get("method") == "bis_standard_only":
        parts.append("This is compounded cattle feed. Check the bag against BIS Type I or Type II, not a photo.")

    asfed = _asfed_span(nutrition)
    if moisture.get("present") and asfed and asfed.get("mean") is not None:
        parts.append(
            f"The moisture probe read {moisture['moisture_pct']}%, so as-fed protein is about {asfed['mean']}%."
            " Moisture is not protein — it only converts the dry-matter table to what the cow actually eats."
        )
    elif moisture.get("present"):
        parts.append(f"The moisture probe read {moisture['moisture_pct']}%.")

    if silage.get("present") and silage.get("flieg_score") is not None:
        parts.append(
            f"Silage pH {silage.get('pH')} and dry matter {silage.get('dm_pct')}%"
            f" give a Flieg score of {silage['flieg_score']} ({silage.get('class', '')})."
        )
    elif silage.get("present"):
        parts.append(f"Silage pH is {silage.get('pH')}. Add a moisture reading to finish the Flieg score.")

    if cv.get("flag"):
        how = "the photo" if cv.get("method") == "hsv_screen" else "your mould mark"
        parts.append(f"Mould showed on {how}. Do not feed this lot; send a sample if you need an aflatoxin test.")
    elif cv.get("method") == "hsv_screen":
        parts.append("The phone photo did not look mouldy on the colour screen. That is not an aflatoxin ppb result.")

    if nir.get("present") and nir.get("used") is False:
        parts.append(
            "The kit colour chip sent 18 bands (410–940 nm). Those bands are stored but not used for protein —"
            " this chip cannot see the protein overtones."
        )
    elif nir.get("used"):
        pred = (nir.get("predictions") or {}).get("cp_pct_dm")
        parts.append(
            f"A 256-band forage NIR estimate is {pred}% CP on the Brazilian calibration only, not Indian oilcake or silage."
        )

    qr = (result.get("modules") or {}).get("qr") or {}
    if qr.get("verified"):
        parts.append("The bag QR matched the Indian tables and the moisture reading.")
    elif qr.get("expired"):
        parts.append(
            "The bag QR is past its expiry date. Mix with a fresher lot or do not feed it as the only bag."
        )
    elif qr.get("present") and qr.get("decoded"):
        parts.append("The bag QR did not match the tables or the moisture probe. Treat the label as untrusted.")

    tips = ration.get("tips_en") or []
    if tips:
        parts.append(tips[0])
    # Include mineral advisory tip if present (usually the 2nd or 3rd tip)
    for tip in tips[1:]:
        if "mineral" in tip.lower() or "calcium" in tip.lower():
            parts.append(tip)
            break

    reasons = farmer.get("reasons_en") or []
    if action != "feed" and reasons:
        parts.append("Main reason: " + reasons[0])

    warns = result.get("sensor_warnings") or []
    if warns:
        parts.append("Check the probe: " + warns[0])

    return " ".join(p.strip() for p in parts if p and p.strip())


def _hindi(name, action, farmer, nutrition, moisture, silage, nir, cv, ration, result) -> str:
    parts = [f"{farmer.get('label_hi', 'खिलाएँ')}। {farmer.get('summary_hi', '')}".strip()]
    parts.append(f"आपने {name} जाँचा।")

    span = _cp_span(nutrition)
    if span and span.get("min") is not None:
        parts.append(
            f"भारतीय तालिका में क्रूड प्रोटीन शुष्क पदार्थ पर लगभग {span['min']}–{span['max']}%"
            f" है (औसत {span['mean']}%)।"
        )
    elif nutrition.get("method") == "bis_standard_only":
        parts.append("यह मिश्रित दाना है। बोरी को BIS टाइप I या II से मिलाएँ, फोटो से प्रोटीन नहीं निकलेगा।")

    asfed = _asfed_span(nutrition)
    if moisture.get("present") and asfed and asfed.get("mean") is not None:
        parts.append(
            f"नमी सेंसर ने {moisture['moisture_pct']}% दिखाया, इसलिए जैसे-खिलाया प्रोटीन लगभग {asfed['mean']}% है।"
            " नमी प्रोटीन नहीं मापती — केवल तालिका को गाय के खाने योग्य आँकड़े में बदलती है।"
        )
    elif moisture.get("present"):
        parts.append(f"नमी सेंसर ने {moisture['moisture_pct']}% दिखाया।")

    if silage.get("present") and silage.get("flieg_score") is not None:
        parts.append(
            f"साइलेज pH {silage.get('pH')} और शुष्क पदार्थ {silage.get('dm_pct')}%"
            f" से Flieg अंक {silage['flieg_score']} ({silage.get('class', '')}) है।"
        )
    elif silage.get("present"):
        parts.append(f"साइलेज का pH {silage.get('pH')} है। Flieg पूरा करने के लिए नमी भी लें।")

    if cv.get("flag"):
        how = "फोटो" if cv.get("method") == "hsv_screen" else "आपके फफूंद निशान"
        parts.append(f"{how} पर फफूंद दिखी। यह लॉट न खिलाएँ; अफलाटॉक्सिन के लिए लैब भेजें।")
    elif cv.get("method") == "hsv_screen":
        parts.append("फोन फोटो पर रंग-जाँच से फफूंद नहीं दिखी। यह अफलाटॉक्सिन ppb नहीं है।")

    if nir.get("present") and nir.get("used") is False:
        parts.append(
            "किट के रंग चिप ने 18 बैंड भेजे (410–940 नैनोमीटर)। ये प्रोटीन के लिए इस्तेमाल नहीं हुए —"
            " इस चिप पर प्रोटीन बैंड नहीं आते।"
        )
    elif nir.get("used"):
        pred = (nir.get("predictions") or {}).get("cp_pct_dm")
        parts.append(
            f"256-बैंड चारा NIR अनुमान {pred}% CP है, केवल ब्राज़ील वाली कैलिब्रेशन पर, भारतीय खली या साइलेज पर नहीं।"
        )

    qr = (result.get("modules") or {}).get("qr") or {}
    if qr.get("verified"):
        parts.append("बोरी के QR ने तालिका और नमी रीडिंग से मेल खाया।")
    elif qr.get("expired"):
        parts.append("बोरी का QR समाप्त तिथि के बाद का है। ताज़ी बोरी के साथ मिलाएँ या अकेले न खिलाएँ।")
    elif qr.get("present") and qr.get("decoded"):
        parts.append("बोरी का QR तालिका या नमी सेंसर से मेल नहीं खाता। लेबल पर भरोसा न करें।")

    tips = ration.get("tips_hi") or []
    if tips:
        parts.append(tips[0])
    for tip in tips[1:]:
        if "खनिज" in tip or "कैल्शियम" in tip:
            parts.append(tip)
            break

    reasons = farmer.get("reasons_hi") or []
    if action != "feed" and reasons:
        parts.append("मुख्य कारण: " + reasons[0])

    warns = result.get("sensor_warnings") or []
    if warns:
        parts.append("सेंसर जाँचें: " + warns[0])

    return " ".join(p.strip() for p in parts if p and p.strip())
