#!/usr/bin/env python3
"""Create a deterministic P67 probe package scaffold around resource.bin.

The generated archive mirrors the metadata and directory structure observed in
the real M2551B1 Mi Fitness cache export. It is a research probe and is not yet
claimed to be accepted by Mi Fitness or installable on the device.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import shutil
import struct
import zlib
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from p67_minimal_builder import CANVAS, build_resource, demo_indexed8


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def indexed8_to_png(width: int, height: int, palette: bytes, indices: bytes) -> bytes:
    if len(palette) != 1024 or len(indices) != width * height:
        raise ValueError("invalid indexed8 data")

    rows = bytearray()
    for y in range(height):
        rows.append(0)
        row = indices[y * width : (y + 1) * width]
        for index in row:
            rows.extend(palette[index * 4 : index * 4 + 4])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + png_chunk(b"IEND", b"")
    )


def capability_json() -> str:
    data = [
        {"name": "protocol", "type": 1, "value": ["1.9.4"]},
        {"name": "resolution", "type": 2, "value": ["XMHD03"]},
        {"name": "region", "type": 2, "value": ["CN"]},
        {"name": "packet", "type": 2, "value": ["BIN"]},
        {"name": "image_compress", "type": 3, "value": ["01"]},
        {"name": "image_fmt", "type": 3, "value": ["00000000000000001"]},
    ]
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def description_xml(package_id: str, name: str, author: str) -> str:
    digest = hashlib.md5(package_id.encode("ascii")).hexdigest()
    return f'''<?xml version="1.0" encoding="utf-8"?>
<watch>
    <shape>square</shape>
    <name>{escape(name)}</name>
    <deviceType>P67</deviceType>
    <version>1.0.0</version>
    <size>336x480</size>
    <author>{escape(author)}</author>
    <pkgName>{package_id}</pkgName>
    <imageFormat>indexed8</imageFormat>
    <imageCompression>true</imageCompression>
    <editorVersion>1.0.0</editorVersion>
    <_recolorEnable>false</_recolorEnable>
    <temperatureUnitType>system</temperatureUnitType>
    <_id>{digest}</_id>
    <imageArrayRamMethod>whole</imageArrayRamMethod>
    <watchfaceType>normal</watchfaceType>
    <watchOS>vela</watchOS>
    <merchantId/>
    <introduce>From-scratch P67 structural probe; not yet device-verified.</introduce>
</watch>
'''


def manifest_xml(package_id: str, name: str, style_name: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Watchface name="@watchfaceName" width="336" height="480" id="{package_id}" SKU="false" compressMethod="RLEReversed" advanced="false" interactive="false" support_literal="false" editable="false">
    <Resources>
        <Translation name="watchfaceName">
            <Item language="zh_CN" str="{escape(name)}"/>
            <Item language="en_US" str="{escape(name)}"/>
        </Translation>
        <Image name="Image1" src="_preview/probe.png" compressMethod="RLEReversed" format="indexed8"/>
        <Image name="Image2" src="probe.png" compressMethod="RLEReversed" format="indexed8"/>
    </Resources>
    <Theme type="normal" name="{escape(style_name)}" bgColor="#000000" isPhotoAlbumWatchface="false" preview="@Image1">
        <Layout ref="@Image2" x="0" y="0"/>
    </Theme>
</Watchface>
'''


def build_package(
    directory: Path,
    package_id: str,
    name: str,
    author: str,
    style_name: str,
) -> dict:
    if directory.exists():
        shutil.rmtree(directory)
    (directory / "preview").mkdir(parents=True)
    (directory / "resources" / "_preview").mkdir(parents=True)

    resource = build_resource(package_id, name, style_name)
    palette, indices = demo_indexed8(*CANVAS)
    png = indexed8_to_png(*CANVAS, palette, indices)

    (directory / "capability.json").write_text(capability_json(), encoding="utf-8")
    (directory / "description.xml").write_text(
        description_xml(package_id, name, author), encoding="utf-8"
    )
    (directory / "manifest.xml").write_text(
        manifest_xml(package_id, name, style_name), encoding="utf-8"
    )
    (directory / "uidmap.map").write_text("Image2: 2000001\n", encoding="utf-8")
    (directory / "resource.bin").write_bytes(resource)
    (directory / "resources" / "probe.png").write_bytes(png)
    (directory / "resources" / "_preview" / "probe.png").write_bytes(png)

    for filename in (
        "preview.png",
        "market-preview.png",
        "style_1_static.png",
        "aod-preview.png",
    ):
        (directory / "preview" / filename).write_bytes(png)

    return {
        "packageId": package_id,
        "resourceSize": len(resource),
        "resourceSha256": hashlib.sha256(resource).hexdigest(),
        "pngSize": len(png),
    }


def zip_package(directory: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="output package directory")
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--package-id", default="991107000001")
    parser.add_argument("--name", default="TIME FLIES PROBE")
    parser.add_argument("--author", default="sep1107")
    parser.add_argument("--style-name", default="Probe")
    args = parser.parse_args()

    if not args.package_id.isdigit():
        raise SystemExit("package ID must contain digits only")

    report = build_package(
        args.output,
        args.package_id,
        args.name,
        args.author,
        args.style_name,
    )
    if args.zip_path:
        zip_package(args.output, args.zip_path)
        report["zip"] = str(args.zip_path)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
