#!/usr/bin/env python3
"""Prepare TIME FLIES resources for the Smart Band 10 Pro workspace.

The original package stores TGA image data in files named with `.png`
extensions. The script therefore calls ImageMagick with explicit `tga:`
prefixes and keeps the original filenames for compatibility.

Normal assets are scaled proportionally. Background images are placed on a
new target canvas without non-uniform stretching.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

GROUPS = (
    "bg",
    "time",
    "date",
    "weather",
    "battery",
    "status",
    "data",
    "smdata",
    "week",
    "level",
    "moon",
)


def parse_canvas(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Canvas must be WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Canvas dimensions must be positive")
    return width, height


def read_tga_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:18]
    if len(header) < 18:
        raise ValueError(f"Invalid TGA file: {path}")
    width = int.from_bytes(header[12:14], "little")
    height = int.from_bytes(header[14:16], "little")
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid TGA dimensions: {path}")
    return width, height


def run_magick(arguments: list[str], source: Path) -> None:
    command = ["magick", *arguments]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ImageMagick was not found. Install it and ensure `magick` is on PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"ImageMagick failed for {source}: {exc.stderr.strip()}"
        ) from exc


def scale_asset(source: Path, destination: Path, scale: float) -> tuple[int, int]:
    original_width, original_height = read_tga_size(source)
    target_width = max(1, round(original_width * scale))
    target_height = max(1, round(original_height * scale))
    destination.parent.mkdir(parents=True, exist_ok=True)

    run_magick(
        [
            f"tga:{source}",
            "-filter",
            "Lanczos",
            "-resize",
            f"{target_width}x{target_height}!",
            "-type",
            "TrueColorAlpha",
            f"tga:{destination}",
        ],
        source,
    )
    return target_width, target_height


def expand_background(
    source: Path,
    destination: Path,
    target_canvas: tuple[int, int],
    background: str,
) -> tuple[int, int]:
    target_width, target_height = target_canvas
    destination.parent.mkdir(parents=True, exist_ok=True)

    run_magick(
        [
            f"tga:{source}",
            "-filter",
            "Lanczos",
            "-resize",
            f"{target_width}x{target_height}",
            "-background",
            background,
            "-gravity",
            "center",
            "-extent",
            f"{target_width}x{target_height}",
            "-type",
            "TrueColorAlpha",
            f"tga:{destination}",
        ],
        source,
    )
    return target_width, target_height


def prepare_assets(
    source_root: Path,
    output_root: Path,
    scale: float,
    target_canvas: tuple[int, int],
    background: str,
) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []

    for group in GROUPS:
        source_group = source_root / group
        if not source_group.is_dir():
            continue

        for source in sorted(source_group.rglob("*.png")):
            relative = source.relative_to(source_root)
            destination = output_root / relative
            original_size = read_tga_size(source)

            if group == "bg" and original_size == (192, 490):
                target_size = expand_background(
                    source,
                    destination,
                    target_canvas=target_canvas,
                    background=background,
                )
                strategy = "proportional fit plus canvas expansion"
            else:
                target_size = scale_asset(source, destination, scale=scale)
                strategy = "proportional scaling"

            manifest.append(
                {
                    "path": relative.as_posix(),
                    "format": "TGA data with .png extension",
                    "strategy": strategy,
                    "original": list(original_size),
                    "prepared": list(target_size),
                }
            )

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Original assets/images directory")
    parser.add_argument("output", type=Path, help="Prepared asset directory")
    parser.add_argument(
        "--target-canvas",
        type=parse_canvas,
        default=(400, 480),
        help="Target canvas, default: 400x480",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.4,
        help="Uniform scale for non-background assets, default: 1.4",
    )
    parser.add_argument(
        "--background",
        default="black",
        help="Background used when expanding the main image",
    )
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    if not args.source.is_dir():
        parser.error(f"Source directory does not exist: {args.source}")
    if args.scale <= 0:
        parser.error("Scale must be positive")

    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = prepare_assets(
        source_root=args.source,
        output_root=args.output,
        scale=args.scale,
        target_canvas=args.target_canvas,
        background=args.background,
    )

    manifest_path = args.output / "asset-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "targetCanvas": list(args.target_canvas),
                "uniformScale": args.scale,
                "assets": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Prepared {len(manifest)} assets")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
