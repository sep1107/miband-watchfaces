#!/usr/bin/env python3
"""Regression test for the known Xiaomi P67 resource.bin header fields."""

from __future__ import annotations

import importlib.util
import struct
from pathlib import Path


def encoded_version(major: int, minor: int, patch: int) -> int:
    return (major << 16) | (minor << 8) | patch


def load_extractor():
    path = Path(__file__).with_name("extract_p67_profile.py")
    spec = importlib.util.spec_from_file_location("extract_p67_profile", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_extractor()
    header = bytearray(128)
    struct.pack_into("<I", header, 0, 0x1234A55A)
    struct.pack_into(
        "<IIIII",
        header,
        4,
        encoded_version(1, 0, 12),
        encoded_version(0, 0, 0),
        encoded_version(0, 0, 0),
        encoded_version(0, 9, 3),
        encoded_version(1, 0, 0),
    )
    header[24] = 2
    header[28] = 3
    header[29] = 4
    struct.pack_into("<H", header, 30, 0x0002)
    struct.pack_into("<I", header, 32, 5465)
    package_id = b"120917384229"
    header[40 : 40 + len(package_id)] = package_id

    parsed = module.parse_resource_header(bytes(header))
    expected = {
        "magic": "0x1234A55A",
        "magicValid": True,
        "watchfaceVersion": "1.0.12",
        "editorVersion": "0.0.0",
        "generatorVersion": "0.0.0",
        "binaryProtocolVersion": "0.9.3",
        "firmwareVersion": "1.0.0",
        "colorGroupCount": 2,
        "themeCount": 3,
        "colorCount": 4,
        "flags": 0x0002,
        "previewImageAddress": 5465,
        "packageId": "120917384229",
        "size": 128,
    }
    for key, value in expected.items():
        actual = parsed.get(key)
        if actual != value:
            raise AssertionError(f"{key}: expected {value!r}, got {actual!r}")

    print("P67 resource.bin header regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
