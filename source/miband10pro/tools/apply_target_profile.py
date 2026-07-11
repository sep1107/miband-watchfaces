#!/usr/bin/env python3
"""Apply a validated target canvas profile to the Band 10 Pro research project."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

VALID_STATUS = {
    "reference-build-chain",
    "reported-hardware",
    "verified-build-target",
}


def replace(pattern: str, replacement: str, text: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not update {label}")
    return updated


def validate_profile(profile: dict) -> tuple[int, int, int, int, str]:
    required = ("schemaVersion", "id", "width", "height", "panelX", "panelPadding", "status", "evidence")
    missing = [key for key in required if key not in profile]
    if missing:
        raise ValueError("Missing profile fields: " + ", ".join(missing))
    if profile["schemaVersion"] != 1:
        raise ValueError("Unsupported profile schemaVersion")

    width = int(profile["width"])
    height = int(profile["height"])
    panel_x = int(profile["panelX"])
    padding = int(profile["panelPadding"])
    profile_id = str(profile["id"])
    status = str(profile["status"])

    if width <= 0 or height <= 0:
        raise ValueError("Canvas dimensions must be positive")
    if panel_x <= 0 or panel_x >= width:
        raise ValueError("panelX must be inside the canvas")
    if padding < 0:
        raise ValueError("panelPadding cannot be negative")
    content_width = width - panel_x - padding - 8
    if content_width < 80:
        raise ValueError(f"Panel content width is too small: {content_width}px")
    if status not in VALID_STATUS:
        raise ValueError(f"Unknown profile status: {status}")
    if not isinstance(profile["evidence"], dict):
        raise ValueError("evidence must be an object")

    return width, height, panel_x, padding, profile_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    width, height, panel_x, padding, profile_id = validate_profile(profile)

    index_path = project / "device/watchface/default-target/index.js"
    text = index_path.read_text(encoding="utf-8")
    text = replace(
        r"const SCREEN_WIDTH = \d+;",
        f"const SCREEN_WIDTH = {width};",
        text,
        "SCREEN_WIDTH",
    )
    text = replace(
        r"const SCREEN_HEIGHT = \d+;",
        f"const SCREEN_HEIGHT = {height};",
        text,
        "SCREEN_HEIGHT",
    )
    text = replace(
        r"const PANEL_X = \d+;",
        f"const PANEL_X = {panel_x};",
        text,
        "PANEL_X",
    )
    text = replace(
        r"const PANEL_PADDING = \d+;",
        f"const PANEL_PADDING = {padding};",
        text,
        "PANEL_PADDING",
    )
    text = replace(
        r"const TARGET_PROFILE = '[^']+';",
        f"const TARGET_PROFILE = '{profile_id}';",
        text,
        "TARGET_PROFILE",
    )
    index_path.write_text(text, encoding="utf-8")

    app_path = project / "device/app.js"
    text = app_path.read_text(encoding="utf-8")
    text = replace(r"getPx\(\d+\)", f"getPx({width})", text, "getPx")
    text = replace(
        r"canvasWidth: \d+",
        f"canvasWidth: {width}",
        text,
        "canvasWidth",
    )
    text = replace(
        r"canvasHeight: \d+",
        f"canvasHeight: {height}",
        text,
        "canvasHeight",
    )
    text = replace(
        r"targetProfile: '[^']+'",
        f"targetProfile: '{profile_id}'",
        text,
        "targetProfile",
    )
    app_path.write_text(text, encoding="utf-8")

    config_path = project / "device/app.json.example"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["designWidth"] = width
    notes = config.setdefault("notes", {})
    notes["primaryTargetProfile"] = profile_id
    notes["primaryCanvas"] = f"{width}x{height}"
    notes["targetProfileStatus"] = profile["status"]
    evidence = profile["evidence"]
    notes["targetHardwareEvidence"] = evidence.get("hardware", "none")
    notes["targetBuildChainEvidence"] = evidence.get("buildChain", "none")
    notes["targetDeviceEvidence"] = evidence.get("deviceTarget", "unverified")
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Applied {profile_id}: {width}x{height}")
    print(f"Profile status: {profile['status']}")
    print(
        "Evidence: hardware={hardware}, build={buildChain}, target={deviceTarget}".format(
            **evidence
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
