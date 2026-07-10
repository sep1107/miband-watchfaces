#!/usr/bin/env python3
"""Prepare TIME FLIES image resources for a new watchface canvas.

The source package uses TGA image data with `.png` filenames. ImageMagick is
therefore invoked with explicit `tga:` prefixes. The script preserves that
convention in the output because the original Zepp OS package expects those
resource names.
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


def read_tga_size(path: Path) -> tuple[int, int]:
    """Read width and height from the 18-byte TGA header."""
    header = path.read_bytes()[:18]
    if len(header) < 18:
        raise ValueError(f"Invalid TGA file: {path}")
    width = int.from_bytes(header[12:14], "little")
    height = int.from_bytes(header[14:16], "little")
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid TGA dimensions: {path}")
    return width, height


def run_magick(source: Path, destination: Path, width: int, height: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "magick",
        f"tga:{source}",
        "-filter",
        "Lanczos",
        "-resize",
        f"{width}x{height}!",
        "-type",
        "TrueColorAlpha",
        f"tga:{destination}",
    ]
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


def prepare_assets(
    source_root: Path,
    output_root: Path,
    source_canvas: tuple[int, int],
    target_canvas: tuple[int, int],
) -> list[dict[str, object]]:
    source_width, source_height = source_canvas
    target_width, target_height = target_canvas
    scale_x = target_width / source_width
    scale_y = target_height / source_height
    manifest: list[dict[str, object]] = []

    for group in GROUPS:
        source_group = source_root / group
        if not source_group.is_dir():
            continue

        for source in sorted(source_group.rglob("*.png")):
            relative = source.relative_to(source_root)
            original_width, original_height = read_tga_size(source)
            scaled_width = max(1, round(original_width * scale_x))
            scaled_height = max(1, round(original_height * scale_y))
            destination = output_root / relative

            run_magick(
                source,
                destination,
                width=scaled_width,
                height=scaled_height,
            )

            manifest.append(
                {
                    "path": relative.as_posix(),
                    "format": "TGA data with .png extension",
                    "original": [original_width, original_height],
                    "scaled": [scaled_width, scaled_height],
                }
            )

    return manifest


def parse_canvas(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("Canvas must use WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Canvas dimensions must be positive")
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the original assets/images directory",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Directory for scaled assets",
    )
    parser.add_argument(
        "--source-canvas",
        type=parse_canvas,
        default=(192, 490),
    )
    parser.add_argument(
        "--target-canvas",
        type=parse_canvas,
        default=(212, 520),
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the output directory before writing",
    )
    args = parser.parse_args()

    if not args.source.is_dir():
        parser.error(f"Source directory does not exist: {args.source}")

    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = prepare_assets(
        args.source,
        args.output,
        args.source_canvas,
        args.target_canvas,
    )
    manifest_path = args.output / "asset-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "sourceCanvas": list(args.source_canvas),
                "targetCanvas": list(args.target_canvas),
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
