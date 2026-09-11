#!/usr/bin/env python3
"""Post a kit reading the same way the ESP32 does. Use this when the board is not wired."""

from __future__ import annotations

import argparse
import json
import urllib.request

CHANNELS = 18


def main() -> None:
    p = argparse.ArgumentParser(description="Simulate SmartFeed ESP32 POST /api/kit")
    p.add_argument("--host", default="http://127.0.0.1:8000")
    p.add_argument("--device", default="sim-kit")
    p.add_argument("--moisture", type=float, default=10.0)
    p.add_argument("--ph", type=float, default=None)
    p.add_argument("--no-as7265x", action="store_true")
    args = p.parse_args()
    body = {
        "device_id": args.device,
        "moisture_pct": args.moisture,
        "moisture_raw": 1800,
    }
    if args.ph is not None:
        body["ph"] = args.ph
        body["ph_raw"] = 1900
    if not args.no_as7265x:
        # Dummy counts so the API records the chip. Pipeline still refuses CP from 18 bands.
        body["as7265x"] = [0.4 + 0.02 * i for i in range(CHANNELS)]
    req = urllib.request.Request(
        args.host.rstrip("/") + "/api/kit",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.read().decode())


if __name__ == "__main__":
    main()
