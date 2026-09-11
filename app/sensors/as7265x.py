"""Stub for the SparkFun-class AS7265x triad (51+52+53).

Read 18 calibrated counts over I2C. Do not map them to Indian CP until
you have paired lab labels on this instrument.
"""

from __future__ import annotations

CHANNELS_NM = (
    410, 435, 460, 485, 510, 535,
    560, 585, 610, 645, 680, 705,
    730, 760, 810, 860, 900, 940,
)


def read_spectrum() -> dict:
    raise NotImplementedError(
        "Wire AS72651 master over I2C and return 18 floats in CHANNELS_NM order."
    )
