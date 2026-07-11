#!/usr/bin/env python3
"""Validate Smart Band target profile JSON files and layout geometry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VALID_STATUS = {
    "reference-build-chain",
    "reported-hardware",
    "verified-build-target",
}
VALID_HARDWARE = {"none", "indirect", "reported", "official"}
VALID_BUILD_CHAIN = {"none", "reference", "tested"}
VALID_DEVICE_TARGET = {"unverified", "reference-only", "verified"}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"profile must be an object: {path}")
    return value


def require_int(profile: dict, key: str, minimum: int = 0) -> int:
    value = profile.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"{key} must be an integer >= {minimum}")
    return value


def require_enum(profile: dict, key: str, choices: set[str]) -> str:
    value = profile.get(key)
    if value not in choices:
        raise ValueError(f"{key} must be one of: {', '.join(sorted(choices))}")
    return value


def validate_profile(path: Path) -> dict:
    profile = load_json(path)

    if profile.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")

    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("id must be a non-empty string")
    if path.stem != profile_id:
        raise ValueError(f"filename must match id ({profile_id}.json)")

    width = require_int(profile, "width", 1)
    height = require_int(profile, "height", 1)
    panel_x = require_int(profile, "panelX", 1)
    panel_padding = require_int(profile, "panelPadding", 0)

    if panel_x >= width:
        raise ValueError("panelX must be inside the canvas")
    content_width = width - panel_x - panel_padding - 8
    if content_width < 80:
        raise ValueError(
            f"right panel content width is too small ({content_width}px; minimum 80px)"
        )
    if height < 320:
        raise ValueError("height is unexpectedly small for this watchface layout")

    status = require_enum(profile, "status", VALID_STATUS)
    evidence = profile.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")

    hardware = require_enum(evidence, "hardware", VALID_HARDWARE)
    build_chain = require_enum(evidence, "buildChain", VALID_BUILD_CHAIN)
    device_target = require_enum(evidence, "deviceTarget", VALID_DEVICE_TARGET)
    sources = evidence.get("sources")
    if not isinstance(sources, list) or not sources or not all(
        isinstance(item, str) and item.strip() for item in sources
    ):
        raise ValueError("evidence.sources must be a non-empty list of strings")

    if status == "verified-build-target" and device_target != "verified":
        raise ValueError("verified-build-target requires deviceTarget=verified")
    if device_target == "verified" and build_chain != "tested":
        raise ValueError("a verified device target requires a tested build chain")
    if status == "reported-hardware" and hardware not in {"reported", "official"}:
        raise ValueError("reported-hardware requires reported or official hardware evidence")

    return {
        "id": profile_id,
        "canvas": f"{width}x{height}",
        "contentWidth": content_width,
        "status": status,
        "hardware": hardware,
        "buildChain": build_chain,
        "deviceTarget": device_target,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "profiles",
        type=Path,
        help="Directory containing target profile JSON files",
    )
    args = parser.parse_args()

    directory = args.profiles.resolve()
    if not directory.is_dir():
        print(f"ERROR: profile directory does not exist: {directory}", file=sys.stderr)
        return 2

    paths = sorted(
        path
        for path in directory.glob("*.json")
        if path.name != "profile.schema.json"
    )
    if not paths:
        print("ERROR: no target profiles found", file=sys.stderr)
        return 2

    results: list[dict] = []
    errors: list[str] = []
    ids: set[str] = set()

    for path in paths:
        try:
            result = validate_profile(path)
            if result["id"] in ids:
                raise ValueError(f"duplicate id: {result['id']}")
            ids.add(result["id"])
            results.append(result)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(results)} target profile(s)")
    for result in results:
        print(
            "- {id}: {canvas}, panel={contentWidth}px, status={status}, "
            "hardware={hardware}, build={buildChain}, target={deviceTarget}".format(
                **result
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
