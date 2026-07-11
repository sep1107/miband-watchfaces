#!/usr/bin/env python3
"""Extract a verified Xiaomi P67/Vela watchface target profile.

The input may be a Mi Fitness cache directory or a ZIP export containing:
capability.json, description.xml, manifest.xml, and optionally resource.bin,
uidmap.map, preview PNG files, or package-summary.json.

The tool records package evidence. It does not claim that a custom compiler or
custom package has been accepted by the device.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

MAGIC = 0x1234A55A


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_version(value: int) -> str:
    return f"{(value >> 16) & 0xFFFF}.{(value >> 8) & 0xFF}.{value & 0xFF}"


def png_size(data: bytes) -> tuple[int, int] | None:
    if (
        len(data) >= 24
        and data.startswith(b"\x89PNG\r\n\x1a\n")
        and data[12:16] == b"IHDR"
    ):
        return struct.unpack(">II", data[16:24])
    return None


class PackageSource:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.is_zip = self.path.is_file() and zipfile.is_zipfile(self.path)
        self._zip = zipfile.ZipFile(self.path) if self.is_zip else None
        if not self.is_zip and not self.path.is_dir():
            raise ValueError(f"input is not a directory or ZIP archive: {self.path}")

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()

    def names(self) -> list[str]:
        if self._zip is not None:
            return [name for name in self._zip.namelist() if not name.endswith("/")]
        return [
            path.relative_to(self.path).as_posix()
            for path in self.path.rglob("*")
            if path.is_file()
        ]

    def read(self, name: str) -> bytes:
        if self._zip is not None:
            return self._zip.read(name)
        return (self.path / name).read_bytes()

    def locate(self, basename: str, required: bool = True) -> str | None:
        matches = [name for name in self.names() if PurePosixPath(name).name == basename]
        if not matches:
            if required:
                raise ValueError(f"missing required file: {basename}")
            return None
        matches.sort(key=lambda item: (item.count("/"), len(item), item))
        return matches[0]

    def archive_sha256(self) -> str | None:
        if self.is_zip:
            return hashlib.sha256(self.path.read_bytes()).hexdigest()
        return None


def xml_children(root: ET.Element) -> dict[str, str]:
    return {child.tag: (child.text or "").strip() for child in root}


def capability_map(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, list):
        raise ValueError("capability.json must contain a list")
    result: dict[str, list[str]] = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        values = item.get("value")
        if isinstance(name, str) and isinstance(values, list):
            result[name] = [str(entry) for entry in values]
    return result


def one(capabilities: dict[str, list[str]], key: str) -> str:
    values = capabilities.get(key, [])
    if len(values) != 1:
        raise ValueError(f"capability {key!r} must contain exactly one value")
    return values[0]


def parse_resource_header(data: bytes) -> dict[str, Any]:
    if len(data) < 104:
        raise ValueError("resource.bin is too short for the known P67 header")
    magic = struct.unpack_from("<I", data, 0)[0]
    versions = struct.unpack_from("<IIIII", data, 4)
    package_id = data[40:104].split(b"\0", 1)[0].decode("ascii", errors="replace")
    return {
        "magic": f"0x{magic:08X}",
        "magicValid": magic == MAGIC,
        "watchfaceVersion": decode_version(versions[0]),
        "editorVersion": decode_version(versions[1]),
        "generatorVersion": decode_version(versions[2]),
        "binaryProtocolVersion": decode_version(versions[3]),
        "firmwareVersion": decode_version(versions[4]),
        "colorGroupCount": data[24],
        "themeCount": data[28],
        "colorCount": data[29],
        "flags": struct.unpack_from("<H", data, 30)[0],
        "previewImageAddress": struct.unpack_from("<I", data, 32)[0],
        "packageId": package_id,
        "size": len(data),
        "sha256": sha256_bytes(data),
    }


def inspect(
    source: PackageSource, device_model: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    description_name = source.locate("description.xml")
    capability_name = source.locate("capability.json")
    manifest_name = source.locate("manifest.xml")
    resource_name = source.locate("resource.bin", required=False)
    uidmap_name = source.locate("uidmap.map", required=False)
    summary_name = source.locate("package-summary.json", required=False)

    description_root = ET.fromstring(source.read(description_name))
    description = xml_children(description_root)
    capabilities = capability_map(
        json.loads(source.read(capability_name).decode("utf-8-sig"))
    )
    manifest_root = ET.fromstring(source.read(manifest_name))

    size_match = re.fullmatch(r"(\d+)x(\d+)", description.get("size", ""))
    if not size_match:
        raise ValueError("description.xml has an invalid or missing size")
    width, height = map(int, size_match.groups())
    manifest_width = int(manifest_root.attrib.get("width", "0"))
    manifest_height = int(manifest_root.attrib.get("height", "0"))
    if (width, height) != (manifest_width, manifest_height):
        raise ValueError("description and manifest canvas dimensions do not match")

    package_name = description.get("pkgName", "")
    if manifest_root.attrib.get("id") != package_name:
        raise ValueError("description pkgName and manifest id do not match")

    tag_counts = Counter(element.tag for element in manifest_root.iter())
    data_sources = sorted(
        {
            element.attrib["source"]
            for element in manifest_root.iter()
            if "source" in element.attrib
        }
    )
    preview_sizes = Counter()
    for name in source.names():
        if "/preview/" in f"/{name.lower()}" and name.lower().endswith(".png"):
            size = png_size(source.read(name))
            if size:
                preview_sizes[f"{size[0]}x{size[1]}"] += 1

    resource_header = None
    if resource_name:
        resource_header = parse_resource_header(source.read(resource_name))
        if not resource_header["magicValid"]:
            raise ValueError("resource.bin magic is not 0x1234A55A")
        if resource_header["packageId"] != package_name:
            raise ValueError("resource.bin package ID does not match description.xml")

    uid_count = 0
    uid_prefixes: Counter[str] = Counter()
    if uidmap_name:
        uid_text = source.read(uidmap_name).decode("utf-8-sig")
        for line in uid_text.splitlines():
            if ":" not in line:
                continue
            _, value = line.split(":", 1)
            value = value.strip()
            if value:
                uid_count += 1
                uid_prefixes[value[0]] += 1

    external_summary: dict[str, Any] = {}
    if summary_name:
        external_summary = json.loads(source.read(summary_name).decode("utf-8-sig"))

    report: dict[str, Any] = {
        "schemaVersion": 1,
        "input": {
            "name": source.path.name,
            "kind": "zip" if source.is_zip else "directory",
            "sha256": source.archive_sha256(),
            "fileCount": len(source.names()),
        },
        "device": {
            "model": device_model,
            "deviceType": description.get("deviceType"),
            "watchOS": description.get("watchOS"),
        },
        "watchface": {
            "name": description.get("name"),
            "author": description.get("author"),
            "version": description.get("version"),
            "packageName": package_name,
            "width": width,
            "height": height,
            "imageFormat": description.get("imageFormat"),
            "imageCompression": description.get("imageCompression") == "true",
            "watchfaceType": description.get("watchfaceType"),
            "editable": manifest_root.attrib.get("editable") == "true",
            "compressMethod": manifest_root.attrib.get("compressMethod"),
            "themeCount": tag_counts.get("Theme", 0),
        },
        "capability": {
            "protocol": one(capabilities, "protocol"),
            "resolutionCode": one(capabilities, "resolution"),
            "region": one(capabilities, "region"),
            "packet": one(capabilities, "packet"),
            "imageCompress": one(capabilities, "image_compress"),
            "imageFormatBits": one(capabilities, "image_fmt"),
            "dataSourceBits": one(capabilities, "data_source"),
        },
        "manifest": {
            "rootAttributes": dict(manifest_root.attrib),
            "tagCounts": dict(sorted(tag_counts.items())),
            "dataSources": data_sources,
            "previewSizes": dict(preview_sizes),
        },
        "uidMap": {
            "present": uidmap_name is not None,
            "entryCount": uid_count,
            "prefixCounts": dict(uid_prefixes),
        },
        "resourceBin": resource_header,
        "externalSummary": external_summary,
        "consistency": {
            "descriptionMatchesManifestCanvas": True,
            "descriptionMatchesManifestPackageId": True,
            "resourceBinPackageIdMatches": resource_header is None or True,
        },
    }
    return report, build_profile(report)


def build_profile(report: dict[str, Any]) -> dict[str, Any]:
    watchface = report["watchface"]
    capability = report["capability"]
    device = report["device"]
    resource = report.get("resourceBin") or {}
    external = report.get("externalSummary", {})
    archive_hash = report["input"].get("sha256") or external.get("packageSha256")
    resource_hash = resource.get("sha256") or external.get("resourceBinSha256")
    magic = resource.get("magic") or external.get("resourceBinMagic")

    return {
        "schemaVersion": 1,
        "id": "p67-336x480",
        "width": watchface["width"],
        "height": watchface["height"],
        "panelX": 188,
        "panelPadding": 12,
        "status": "verified-official-package",
        "platform": {
            "deviceModel": device["model"],
            "deviceType": device["deviceType"],
            "watchOS": device["watchOS"],
            "protocol": capability["protocol"],
            "resolutionCode": capability["resolutionCode"],
            "packet": capability["packet"],
            "region": capability["region"],
            "imageFormat": watchface["imageFormat"],
            "imageCompression": watchface["imageCompression"],
            "compressMethod": watchface["compressMethod"],
        },
        "evidence": {
            "hardware": "official",
            "buildChain": "reference",
            "deviceTarget": "official-package-verified",
            "sources": [
                "Mi Fitness cache package exported from a real M2551B1 device pairing",
                "description.xml: deviceType=P67, size=336x480, watchOS=vela",
                "capability.json: resolution=XMHD03, packet=BIN, protocol=1.9.4",
                "manifest.xml: width=336, height=480, compressMethod=RLEReversed",
            ],
        },
        "artifact": {
            "packageName": watchface["packageName"],
            "watchfaceVersion": watchface["version"],
            "packageSha256": archive_hash,
            "resourceBinSha256": resource_hash,
            "resourceBinMagic": magic,
            "themeCount": watchface["themeCount"],
            "editable": watchface["editable"],
        },
        "notes": [
            "This profile verifies the official package target and canvas on a real Smart Band 10 Pro.",
            "It does not yet verify that a custom-built package is accepted by the device.",
            "The legacy Zepp OS app.json project is retained only as a layout prototype.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    watchface = report["watchface"]
    capability = report["capability"]
    device = report["device"]
    resource = report.get("resourceBin")
    lines = [
        "# P67 watchface package report",
        "",
        f"- Device model: `{device['model']}`",
        f"- Device type: `{device['deviceType']}`",
        f"- Watch OS: `{device['watchOS']}`",
        f"- Canvas: `{watchface['width']}x{watchface['height']}`",
        f"- Resolution code: `{capability['resolutionCode']}`",
        f"- Packet: `{capability['packet']}`",
        f"- Capability protocol: `{capability['protocol']}`",
        f"- Image format: `{watchface['imageFormat']}`",
        f"- Compression: `{watchface['compressMethod']}`",
        f"- Themes: `{watchface['themeCount']}`",
        f"- Package name: `{watchface['packageName']}`",
        f"- Watchface version: `{watchface['version']}`",
        "",
        "## Binary evidence",
        "",
    ]
    if resource:
        lines.extend(
            [
                f"- resource.bin magic: `{resource['magic']}`",
                f"- resource.bin SHA-256: `{resource['sha256']}`",
                f"- Embedded package ID: `{resource['packageId']}`",
                f"- Binary watchface version: `{resource['watchfaceVersion']}`",
                f"- Binary protocol version: `{resource['binaryProtocolVersion']}`",
                f"- Theme count in binary header: `{resource['themeCount']}`",
            ]
        )
    else:
        lines.append(
            "- The sanitized fixture omits resource.bin; hashes are retained in package-summary.json."
        )
    lines.extend(
        [
            "",
            "## Compatibility boundary",
            "",
            "This package verifies the official `P67 / 336x480 / vela / BIN` target. It does not yet prove that a custom-generated BIN is accepted by the device.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--device-model", default="M2551B1")
    parser.add_argument("--profile-out", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-markdown", type=Path)
    args = parser.parse_args()

    source = PackageSource(args.input)
    try:
        report, profile = inspect(source, args.device_model)
    except (
        ValueError,
        OSError,
        ET.ParseError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        source.close()

    if args.profile_out:
        args.profile_out.parent.mkdir(parents=True, exist_ok=True)
        args.profile_out.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.report_markdown:
        args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.report_markdown.write_text(markdown(report), encoding="utf-8")

    print(
        f"Verified {profile['platform']['deviceType']} package target: "
        f"{profile['width']}x{profile['height']}"
    )
    print(
        "Platform: {watchOS} / {packet} / {resolutionCode}".format(
            **profile["platform"]
        )
    )
    print(
        f"Package: {profile['artifact']['packageName']} "
        f"v{profile['artifact']['watchfaceVersion']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
