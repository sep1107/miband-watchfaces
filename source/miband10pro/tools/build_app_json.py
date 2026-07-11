#!/usr/bin/env python3
"""Generate a legacy Zepp OS layout-prototype app.json.

This helper is not the P67/Vela BIN compiler. The verified Smart Band 10 Pro
package path is documented by the p67-336x480 target profile.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("template", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--platform-name", required=True)
    parser.add_argument(
        "--device-source",
        type=int,
        action="append",
        required=True,
        help="Legacy Zepp OS deviceSource; not used by the P67/Vela BIN target",
    )
    parser.add_argument("--design-width", type=int, default=336)
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()

    if args.design_width != 336:
        parser.error("--design-width must be 336 for this project")
    if any(value < 0 for value in args.device_source):
        parser.error("--device-source must be a non-negative integer")

    config = json.loads(args.template.read_text(encoding="utf-8"))
    config["designWidth"] = args.design_width
    config["platforms"] = [
        {"name": args.platform_name, "deviceSource": value}
        for value in args.device_source
    ]
    config.pop("notes", None)
    config["debug"] = not args.release

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated legacy layout-prototype config: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
