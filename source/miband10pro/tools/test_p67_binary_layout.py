#!/usr/bin/env python3
"""Regression test for the P67 extended theme and record-table layout."""

from __future__ import annotations

import importlib.util
import struct
from pathlib import Path


def encoded_version(major: int, minor: int, patch: int) -> int:
    return (major << 16) | (minor << 8) | patch


def load_inspector():
    path = Path(__file__).with_name("inspect_p67_binary.py")
    spec = importlib.util.spec_from_file_location("inspect_p67_binary", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_fixture() -> bytes:
    header_size = 168
    theme_size = 176
    record_size = 16
    record_start = header_size + theme_size
    raw_start = record_start + record_size
    data = bytearray(raw_start + 16)

    struct.pack_into("<I", data, 0, 0x1234A55A)
    struct.pack_into(
        "<IIIII",
        data,
        4,
        encoded_version(1, 0, 0),
        encoded_version(0, 0, 0),
        encoded_version(0, 0, 0),
        encoded_version(0, 9, 3),
        encoded_version(1, 0, 0),
    )
    data[28] = 1
    struct.pack_into("<H", data, 30, 0x0002)
    package_id = b"120000000001"
    data[40 : 40 + len(package_id)] = package_id

    theme = header_size
    struct.pack_into("<II", data, theme, 0x80000000, raw_start)
    for record_type in range(10):
        count = 1 if record_type == 0 else 0
        address = record_start if count else raw_start
        struct.pack_into("<II", data, theme + 8 + record_type * 8, count, address)

    extension = theme + 88
    struct.pack_into("<IIII", data, extension, 0, raw_start, 0, raw_start)
    style_name = "测试样式".encode("utf-8")
    data[extension + 16 : extension + 16 + len(style_name)] = style_name

    struct.pack_into("<IIII", data, record_start, 0x00000000, 0, raw_start, 16)
    struct.pack_into("<IHHII", data, raw_start, 0x02000001, 1, 2, 0, 0)
    return bytes(data)


def main() -> int:
    module = load_inspector()
    report = module.inspect_binary(build_fixture())

    assert report["format"]["headerSize"] == 168
    assert report["format"]["themeSize"] == 176
    assert report["format"]["themeExtensionSize"] == 88
    assert report["format"]["recordSize"] == 16
    assert report["format"]["recordAreaStart"] == 344
    assert report["format"]["rawDataStart"] == 360
    assert report["themes"][0]["extension"]["styleName"] == "测试样式"
    assert report["recordTypeCounts"] == {"layout": 1}
    assert report["recordCount"] == 1
    assert report["records"][0]["payload"]["resourceUid"] == "0x02000001"
    assert report["records"][0]["payload"]["x"] == 1
    assert report["records"][0]["payload"]["y"] == 2
    assert report["validation"]["errors"] == []

    print("P67 extended theme and record-table regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
