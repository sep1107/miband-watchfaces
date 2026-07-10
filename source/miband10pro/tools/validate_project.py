#!/usr/bin/env python3
"""Validate the TIME FLIES Smart Band 10 Pro source project."""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(errors, f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(errors, f"Invalid JSON in {path}: {exc}")
    return {}


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("missing PNG IHDR")
    return struct.unpack(">II", data[16:24])


def check_javascript(path: Path, errors: list[str], warnings: list[str]) -> None:
    if not path.is_file():
        fail(errors, f"Missing JavaScript file: {path}")
        return
    node = shutil.which("node")
    if not node:
        warnings.append("Node.js not found; JavaScript syntax check skipped")
        return
    result = subprocess.run(
        [node, "--check", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(errors, f"JavaScript syntax error in {path}: {result.stderr.strip()}")


def validate_config(project: Path, errors: list[str]) -> None:
    config_path = project / "device" / "app.json.example"
    config = read_json(config_path, errors)
    if not config:
        return

    app = config.get("app", {})
    if app.get("appType") != "watchface":
        fail(errors, "app.appType must be 'watchface'")

    watchface = config.get("module", {}).get("watchface", {})
    if watchface.get("path") != "watchface/default-target/index":
        fail(errors, "module.watchface.path must be watchface/default-target/index")

    design_width = config.get("designWidth")
    if not isinstance(design_width, int) or design_width <= 0:
        fail(errors, "designWidth must be a positive integer")

    notes = config.get("notes", {})
    if not notes.get("deviceSource"):
        fail(errors, "notes.deviceSource must document the unresolved target")


def validate_assets(
    project: Path,
    source_only: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[int, int]:
    required_path = project / "required-assets.json"
    required_data = read_json(required_path, errors)
    required = required_data.get("runtimeRequiredAssets", []) if required_data else []
    if not isinstance(required, list) or not required:
        fail(errors, "required-assets.json must contain runtimeRequiredAssets")
        return 0, 0

    assets_root = project / "device" / "assets"
    if source_only and not assets_root.is_dir():
        warnings.append(
            "Assets are not present in the GitHub text-only checkout; strict asset validation skipped"
        )
        return len(required), 0

    missing: list[str] = []
    checked = 0
    for relative in required:
        path = assets_root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        try:
            width, height = png_dimensions(path)
            if width <= 0 or height <= 0:
                raise ValueError("invalid dimensions")
        except ValueError as exc:
            fail(errors, f"Invalid asset {relative}: {exc}")
            continue
        checked += 1

    if missing:
        fail(errors, "Missing runtime assets: " + ", ".join(missing))

    full_pngs = list(assets_root.rglob("*.png")) if assets_root.is_dir() else []
    for path in full_pngs:
        try:
            png_dimensions(path)
        except ValueError as exc:
            fail(errors, f"Invalid PNG {path.relative_to(assets_root)}: {exc}")

    return len(required), checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, help="Project root containing device/")
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Allow the GitHub checkout to omit binary assets",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not project.is_dir():
        print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
        return 2

    validate_config(project, errors)
    check_javascript(project / "device" / "app.js", errors, warnings)
    check_javascript(
        project / "device" / "watchface" / "default-target" / "index.js",
        errors,
        warnings,
    )
    required_count, checked_count = validate_assets(
        project, args.source_only, errors, warnings
    )

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1

    print("Validation passed")
    print(f"Required runtime assets: {required_count}")
    if checked_count:
        print(f"Validated runtime assets: {checked_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
