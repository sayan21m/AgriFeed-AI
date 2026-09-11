"""CLI: python -m smartfeed.cli mustard cake --moisture 10"""

from __future__ import annotations

import argparse
import json
import sys

from smartfeed.pipeline import assess
from smartfeed.validate import SensorRangeError


def main() -> None:
    p = argparse.ArgumentParser(description="SmartFeed India village-kit assess")
    p.add_argument("ingredient", nargs="+")
    p.add_argument("--form", choices=["ingredient", "silage", "compounded"])
    p.add_argument("--moisture", type=float)
    p.add_argument("--ph", type=float)
    p.add_argument("--urea-yellow", type=float)
    p.add_argument("--mould", action="store_true")
    p.add_argument("--image")
    p.add_argument("--aia", type=float, help="acid-insoluble ash %% from a lab or mini-kit")
    p.add_argument("--grit-ml", type=float, help="settled grit in the jar test")
    p.add_argument("--sample-g", type=float, help="sample weight for the jar test")
    p.add_argument("--lang", choices=["en", "hi"], default="en")
    p.add_argument("--json", action="store_true", help="print the full result instead of a farmer card")
    args = p.parse_args()
    try:
        result = assess(
            " ".join(args.ingredient),
            form=args.form,
            moisture_pct=args.moisture,
            ph=args.ph,
            urea_yellow_area_pct=args.urea_yellow,
            visible_mould=True if args.mould else None,
            image_path=args.image,
            aia_pct=args.aia,
            grit_settled_ml=args.grit_ml,
            sample_g=args.sample_g,
        )
    except SensorRangeError as exc:
        sys.exit(f"Bad reading: {exc}")

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    card = result["farmer"]
    ration = result["ration"]
    print(card[f"label_{args.lang}"].upper())
    print(card[f"summary_{args.lang}"])
    spoken = (result.get("spoken") or {}).get(args.lang)
    if spoken:
        print()
        print(spoken)
    for line in card[f"reasons_{args.lang}"]:
        print(f"  - {line}")
    for line in card[f"other_flags_{args.lang}"]:
        print(f"  · {line}")
    print(f"\n{ration[f'role_{args.lang}']}")
    for tip in ration[f"tips_{args.lang}"]:
        print(f"  - {tip}")
    for warn in result["sensor_warnings"]:
        print(f"\n! {warn}")


if __name__ == "__main__":
    main()
