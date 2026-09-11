"""What to do with this feed in today's ration.

This is *not* a formulated ration. It reads the feed class and the looked-up CP
range and says what job this ingredient does, and what it cannot do alone.
A lactating crossbred cow's total mixed ration is normally built around
12-16% CP on a dry-matter basis, so a single ingredient is judged against that.
"""

from __future__ import annotations

RATION_CP_TARGET_PCT_DM = (12.0, 16.0)

ROLE = {
    "crop_residue": ("Filler roughage", "भराव चारा"),
    "hay": ("Roughage", "सूखा चारा"),
    "silage": ("Succulent roughage", "रसीला चारा"),
    "grains": ("Energy source", "ऊर्जा स्रोत"),
    "byproducts": ("Mixed energy / fibre", "मिश्रित ऊर्जा व रेशा"),
    "oilcakes": ("Protein source", "प्रोटीन स्रोत"),
    "molasses": ("Energy / palatability", "ऊर्जा व स्वाद"),
    "compounded": ("Balanced concentrate", "संतुलित दाना"),
}


def _cp_mean(nutrition: dict):
    span = (nutrition.get("nutrients_pct_dm") or {}).get("crude_protein_pct_dm")
    return None if not span else span.get("mean")


def ration_advice(nutrition: dict) -> dict:
    feed_class = nutrition.get("feed_class")
    role_en, role_hi = ROLE.get(feed_class, ("Feed ingredient", "चारा सामग्री"))
    cp = _cp_mean(nutrition)
    lo, hi = RATION_CP_TARGET_PCT_DM

    tips_en: list[str] = []
    tips_hi: list[str] = []

    if nutrition.get("method") == "bis_standard_only":
        tips_en.append(f"Check the bag label against BIS: Type I needs CP >= {22}% DM.")
        tips_hi.append("बोरी के लेबल को BIS से मिलाएँ: टाइप I में CP कम से कम 22% DM।")
    elif cp is None:
        tips_en.append("No protein figure for this name. Pick the closest listed feed.")
        tips_hi.append("इस नाम का प्रोटीन आँकड़ा नहीं है। सूची से मिलता-जुलता चारा चुनें।")
    elif cp < 6:
        tips_en.append(
            f"Only about {cp}% CP. Well below the {lo}-{hi}% a milking ration needs, "
            "so it cannot be the whole feed. Add a cake or compounded feed and green fodder."
        )
        tips_hi.append(
            f"केवल लगभग {cp}% प्रोटीन। दुधारू राशन के {lo}-{hi}% से बहुत कम, "
            "अकेले न खिलाएँ। खली या दाना और हरा चारा मिलाएँ।"
        )
    elif cp < lo:
        tips_en.append(f"About {cp}% CP, under the {lo}-{hi}% ration target. Pair with a protein feed.")
        tips_hi.append(f"लगभग {cp}% प्रोटीन, {lo}-{hi}% लक्ष्य से कम। प्रोटीन वाला चारा साथ दें।")
    elif cp > 25:
        tips_en.append(
            f"Protein-rich at about {cp}% CP. Feed as a measured share of the concentrate, not free choice."
        )
        tips_hi.append(f"लगभग {cp}% प्रोटीन, बहुत अधिक। नापकर दाने के हिस्से के रूप में दें, खुला नहीं।")
    else:
        tips_en.append(f"About {cp}% CP, inside the {lo}-{hi}% ration band.")
        tips_hi.append(f"लगभग {cp}% प्रोटीन, {lo}-{hi}% राशन सीमा के भीतर।")

    if feed_class == "silage":
        tips_en.append("Keep the silo face tight and clean after taking today's cut.")
        tips_hi.append("आज का साइलेज निकालने के बाद गड्ढे का मुँह कसकर बंद रखें।")

    if nutrition.get("method") == "best_cv_name_model":
        tips_en.append("This name was not in the Indian tables, so the figure is a guess from the name.")
        tips_hi.append("यह नाम भारतीय तालिका में नहीं था, इसलिए यह आँकड़ा नाम से लगाया गया अनुमान है।")

    # --- Mineral deficiency advisory ---
    if feed_class in {"crop_residue", "hay"}:
        tips_en.append(
            "This roughage is low in Calcium and Phosphorus. "
            "Add 50–100 g Area-Specific Mineral Mixture (ASMM) daily per animal."
        )
        tips_hi.append(
            "इस चारे में कैल्शियम और फ़ॉस्फ़ोरस कम है। "
            "प्रति पशु प्रतिदिन 50–100 ग्राम क्षेत्र-विशिष्ट खनिज मिश्रण (ASMM) दें।"
        )
    elif feed_class == "grains":
        tips_en.append(
            "Grain-heavy diets lack minerals. "
            "Ensure a mineral mixture is part of the daily ration."
        )
        tips_hi.append(
            "अनाज-प्रधान आहार में खनिज कम होते हैं। "
            "दैनिक राशन में खनिज मिश्रण अवश्य शामिल करें।"
        )
    elif feed_class == "oilcakes" and cp is not None and cp > 30:
        tips_en.append(
            "High-protein cakes can have a Calcium–Phosphorus imbalance. "
            "Balance with a mineral supplement."
        )
        tips_hi.append(
            "अधिक प्रोटीन वाली खली में कैल्शियम-फ़ॉस्फ़ोरस असंतुलन हो सकता है। "
            "खनिज पूरक के साथ संतुलित करें।"
        )

    return {
        "role_en": role_en,
        "role_hi": role_hi,
        "cp_pct_dm_mean": cp,
        "ration_cp_target_pct_dm": [lo, hi],
        "tips_en": tips_en,
        "tips_hi": tips_hi,
        "note": "Guidance for one ingredient. It does not replace a nutritionist's balanced ration.",
    }
