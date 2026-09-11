"""SmartFeed India — village-kit models and fused pipeline."""

from smartfeed.pipeline import assess
from smartfeed.adulteration import assess_sand
from smartfeed.aflatoxin import assess_aflatoxin
from smartfeed.cv_mould import assess_image, mould_score
from smartfeed.moisture import assess_moisture, as_fed
from smartfeed.nir import assess_nir
from smartfeed.nutrition import assess_nutrition
from smartfeed.ration import ration_advice
from smartfeed.speak import spoken_advice
from smartfeed.silage import assess_silage, flieg_score
from smartfeed.urea import assess_urea
from smartfeed.validate import SensorRangeError

__all__ = [
    "SensorRangeError",
    "assess",
    "assess_aflatoxin",
    "assess_image",
    "assess_moisture",
    "assess_nir",
    "assess_nutrition",
    "assess_sand",
    "assess_silage",
    "assess_urea",
    "as_fed",
    "flieg_score",
    "mould_score",
    "ration_advice",
    "spoken_advice",
]
