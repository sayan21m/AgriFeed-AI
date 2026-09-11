"""Farmer-facing EN/HI text for feed / dilute / reject."""

from __future__ import annotations

ACTION = {
    "feed": {
        "en": "Feed",
        "hi": "खिलाएँ",
        "summary_en": "Safe to feed. Use the protein range below when mixing today's ration.",
        "summary_hi": "खिलाना सुरक्षित है। आज के राशन में नीचे दी गई प्रोटीन सीमा का उपयोग करें।",
    },
    "dilute": {
        "en": "Dilute / mix",
        "hi": "मिलाकर खिलाएँ",
        "summary_en": "Do not feed this bag or pit alone. Mix with a safer lot and use soon.",
        "summary_hi": "इस बोरी या साइलेज को अकेले न खिलाएँ। बेहतर चारे के साथ मिलाएँ और जल्दी उपयोग करें।",
    },
    "reject": {
        "en": "Reject",
        "hi": "न खिलाएँ",
        "summary_en": "Do not feed. Discard or send a sample to the union lab.",
        "summary_hi": "न खिलाएँ। फेंक दें या यूनियन लैब में नमूना भेजें।",
    },
}

REASON = {
    "urea at or above BIS 1%": {
        "en": "Urea screen at or above the BIS 1% limit.",
        "hi": "यूरिया जाँच BIS की 1% सीमा पर या उससे अधिक है।",
    },
    "4-DMAB yellow — suspect urea": {
        "en": "4-DMAB strip turned yellow — suspect added urea.",
        "hi": "4-DMAB पट्टी पीली हुई — मिलावटी यूरिया की आशंका।",
    },
    "visible mould": {
        "en": "Visible mould on the sample.",
        "hi": "नमूने पर फफूंद दिख रही है।",
    },
    "compounded-feed moisture above BIS 11%": {
        "en": "Compounded feed moisture above BIS 11%. Store dry or use soon.",
        "hi": "मिश्रित दाने में नमी BIS 11% से अधिक है। सुखाकर रखें या जल्दी खिलाएँ।",
    },
    "high-AF-risk ingredient plus mould": {
        "en": "High aflatoxin-risk ingredient plus mould. Need a lab or strip test.",
        "hi": "अफलाटॉक्सिन-जोखिम वाला चारा और फफूंद। लैब या स्ट्रिप जाँच चाहिए।",
    },
    "silage too wet — effluent and clostridia risk": {
        "en": "Silage is very wet. Effluent runs off and butyric spoilage is likely.",
        "hi": "साइलेज बहुत गीला है। रस बहने और खराब सड़न का खतरा है।",
    },
    "acid-insoluble ash above the BIS sand limit": {
        "en": "Acid-insoluble ash above the BIS limit — sand or soil in the feed.",
        "hi": "अम्ल-अघुलनशील राख BIS सीमा से अधिक — चारे में रेत या मिट्टी है।",
    },
    "grit settled in the jar test — suspect sand": {
        "en": "Grit settled in the water jar — suspect sand. Get an AIA test.",
        "hi": "पानी के जार में रेत बैठी — मिलावट की आशंका। AIA जाँच कराएँ।",
    },
    "no reject/dilute trigger from sensors + tables": {
        "en": "No reject or dilute trigger from the sensors and tables.",
        "hi": "सेंसर और तालिका से कोई अस्वीकार संकेत नहीं।",
    },
}

# Reasons that carry a measured number, so they are matched on their opening words.
PREFIXES = {
    "silage Flieg": {
        "en": "Silage fermentation score is low.",
        "hi": "साइलेज का किण्वन अंक कम है।",
    },
    "silage pH": {
        "en": "Silage pH is above 4.2 on low dry matter — it never soured properly.",
        "hi": "कम शुष्क पदार्थ पर साइलेज का pH 4.2 से ऊपर है — ठीक से खट्टा नहीं हुआ।",
    },
}


def translate_reason(reason: str, lang: str) -> str:
    if reason in REASON:
        return REASON[reason][lang]
    for prefix, pack in PREFIXES.items():
        if reason.startswith(prefix):
            return f"{pack[lang]} ({reason})" if lang == "hi" else f"{pack['en']} ({reason})"
    return reason


def farmer_card(decision: dict) -> dict:
    action = decision.get("action", "feed")
    pack = ACTION.get(action, ACTION["feed"])
    other = decision.get("other_flags", [])
    return {
        "action": action,
        "label_en": pack["en"],
        "label_hi": pack["hi"],
        "summary_en": pack["summary_en"],
        "summary_hi": pack["summary_hi"],
        "reasons_en": [translate_reason(r, "en") for r in decision.get("reasons", [])],
        "reasons_hi": [translate_reason(r, "hi") for r in decision.get("reasons", [])],
        "other_flags_en": [translate_reason(r, "en") for r in other],
        "other_flags_hi": [translate_reason(r, "hi") for r in other],
    }
