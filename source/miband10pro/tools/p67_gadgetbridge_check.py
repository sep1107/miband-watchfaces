#!/usr/bin/env python3
"""Check whether a P67 resource.bin matches Gadgetbridge import rules."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

MAX_SIZE = 128 * 1024 * 1024
ID_OFFSET = 0x28
NAME_OFFSET = 0x68
PREVIEW_OFFSET = 0x20
I18N_OFFSET_FIELD = 0x74
I18N_SIZE_FIELD = 0x78
IMAGE_HEADER_SIZE = 12


def nul_text(data: bytes, offset: int, encoding: str = "utf-8") -> str | None:
    if not 0 <= offset < len(data):
        return None
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    raw = data[offset:end]
    if not raw:
        return None
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError:
        return None


def inspect_i18n(data: bytes) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []
    table_offset = struct.unpack_from("<I", data, I18N_OFFSET_FIELD)[0]
    table_size = struct.unpack_from("<I", data, I18N_SIZE_FIELD)[0]
    report: dict[str, object] = {
        "offset": table_offset,
        "size": table_size,
        "localeMask": None,
        "localeCount": None,
    }
    if table_size < 8:
        errors.append("localized name table is smaller than 8 bytes")
        return report, errors
    if table_offset + table_size > len(data):
        errors.append("localized name table is outside the file")
        return report, errors
    locale_mask = struct.unpack_from("<Q", data, table_offset)[0]
    locale_count = locale_mask.bit_count()
    report["localeMask"] = f"0x{locale_mask:016X}"
    report["localeCount"] = locale_count
    minimum = 8 + locale_count * 4
    if table_size < minimum:
        errors.append("localized name table is shorter than its length directory")
        return report, errors
    lengths = [
        struct.unpack_from("<I", data, table_offset + 8 + index * 4)[0]
        for index in range(locale_count)
    ]
    if minimum + sum(lengths) > table_size:
        errors.append("localized name strings exceed the declared table size")
    report["stringLengths"] = lengths
    return report, errors


def inspect(data: bytes) -> dict[str, object]:
    errors: list[str] = []
    if len(data) > MAX_SIZE:
        errors.append("file exceeds Gadgetbridge size limit")
    if len(data) <= NAME_OFFSET + 4:
        errors.append("file is too short")
        return {"errors": errors}
    if data[:2] != b"\x5a\xa5":
        errors.append("watchface magic is not 5A A5")

    package_id = nul_text(data, ID_OFFSET, "ascii")
    if not package_id or not package_id.isdigit():
        errors.append("numeric package ID missing at 0x28")

    preview = struct.unpack_from("<I", data, PREVIEW_OFFSET)[0]
    if preview and preview + IMAGE_HEADER_SIZE > len(data):
        errors.append("preview header is outside the file")

    localized = data[NAME_OFFSET : NAME_OFFSET + 4] == b"\xff\xff\xff\xff"
    name = None if localized else nul_text(data, NAME_OFFSET)
    localized_name = None
    if localized:
        localized_name, i18n_errors = inspect_i18n(data)
        errors.extend(i18n_errors)
    elif not name:
        errors.append("name missing at 0x68")

    return {
        "packageId": package_id,
        "name": name,
        "localizedName": localized,
        "localizedNameTable": localized_name,
        "previewOffset": preview,
        "size": len(data),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_bin", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = inspect(args.resource_bin.read_bytes())
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
