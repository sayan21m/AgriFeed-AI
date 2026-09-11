"""Ingredient name normalisation used by the lookup model."""

from __future__ import annotations

import re

REPLACEMENTS = (
    ("rice bran (de-oiled)", "deoiled rice bran"),
    ("rice bran (deoiled)", "deoiled rice bran"),
    ("cottonseed meal (undecorticated)", "cottonseed cake undecorticated"),
    ("cottonseed meal (decorticated)", "cottonseed meal"),
    ("cottonseed oil cake (undecorticated)", "cottonseed cake undecorticated"),
    ("un-decorticated cottonseed cake", "cottonseed cake undecorticated"),
    ("sunflower meal (undecorticated)", "sunflower meal"),
    ("mustard seed cake", "mustard cake"),
    ("rapeseed oil cake", "mustard cake"),
    ("rape seed cake", "mustard cake"),
    ("rapeseed meal", "mustard meal"),
    ("deoiled mustard cake", "mustard meal"),
    ("groundnut oil cake", "groundnut cake"),
    ("groundnut meal", "groundnut meal"),
    ("soyabean meal", "soybean meal"),
    ("coconut oil cake", "coconut cake"),
    ("sesame oil cake", "til cake"),
    ("til oil cake", "til cake"),
    ("linseed oil cake", "linseed cake"),
    ("wheat bran a", "wheat bran"),
    ("wheat bran b", "wheat bran"),
    ("maize grain", "maize"),
    ("barley grain", "barley"),
    ("oat grain", "oats"),
    ("wheat grain", "wheat"),
    ("broken rice", "rice"),
    ("rice grit", "rice"),
    ("cane molasses", "molasses"),
    ("jowar", "sorghum"),
    ("cotton seed cake", "cottonseed cake"),
    ("dorb", "deoiled rice bran"),
    ("gnc", "groundnut cake"),
    ("sarson khali", "mustard cake"),
    ("sarson cake", "mustard cake"),
    ("binola khali", "cottonseed cake undecorticated"),
    ("wheat chokar", "wheat bran"),
    ("chokar", "wheat bran"),
    ("gram flour", "gram"),
    ("tuar chuni", "arhar chuni"),
)

FARMER_ALIASES = {
    "maize silage": "maize silage",
    "corn silage": "maize silage",
    "wheat silage": "wheat silage",
    "compounded cattle feed": "compounded feed",
    "cattle feed": "compounded feed",
    "oat": "oats",
}

KEYWORD_TAGS = (
    "silage",
    "straw",
    "stover",
    "bhusa",
    "hay",
    "molasses",
    "chuni",
    "bran",
    "polish",
    "husk",
    "hull",
    "meal",
    "cake",
    "khali",
    "grain",
)


def normalize_name(name: str) -> str:
    text = str(name).strip().lower()
    text = text.replace("de-oiled", "deoiled").replace("soyabean", "soybean")
    text = re.sub(r"[()]", " ", text)
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("de oiled", "deoiled")
    if text in FARMER_ALIASES:
        return FARMER_ALIASES[text]
    for src, dst in REPLACEMENTS:
        if text == src or text.startswith(src + " "):
            return (dst + text[len(src) :]).strip()
    return text


def enrich(text: str) -> str:
    s = str(text).strip().lower()
    tags = [k for k in KEYWORD_TAGS if k in s]
    return (" ".join(tags) + " " + s).strip()
