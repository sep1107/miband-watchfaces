#!/usr/bin/env python3
"""Regression test for the P67 probe package scaffold."""
from __future__ import annotations

import json
import struct
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from p67_probe_package import build_package, zip_package


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "probe"
        report = build_package(
            root,
            "991107000001",
            "TIME FLIES PROBE",
            "sep1107",
            "Probe",
        )
        assert report["resourceSize"] > 1000

        required = {
            "capability.json",
            "description.xml",
            "manifest.xml",
            "uidmap.map",
            "resource.bin",
            "preview/preview.png",
            "resources/probe.png",
            "resources/_preview/probe.png",
        }
        present = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        }
        assert required <= present

        capabilities = json.loads((root / "capability.json").read_text())
        capability_map = {
            item["name"]: item["value"][0] for item in capabilities
        }
        assert capability_map["resolution"] == "XMHD03"
        assert capability_map["packet"] == "BIN"

        description = ET.parse(root / "description.xml").getroot()
        assert description.findtext("deviceType") == "P67"
        assert description.findtext("size") == "336x480"
        assert description.findtext("watchOS") == "vela"
        assert description.findtext("pkgName") == "991107000001"

        manifest = ET.parse(root / "manifest.xml").getroot()
        assert manifest.attrib["width"] == "336"
        assert manifest.attrib["height"] == "480"
        images = manifest.findall("./Resources/Image")
        assert [image.attrib["name"] for image in images] == ["Image1", "Image2"]
        assert (root / "uidmap.map").read_text() == "Image2: 2000001\n"

        resource = (root / "resource.bin").read_bytes()
        record_start = 168 + 176
        image_uid = struct.unpack_from("<I", resource, record_start + 16)[0]
        assert image_uid == 0x02000001

        archive = Path(temp) / "probe.zip"
        zip_package(root, archive)
        with zipfile.ZipFile(archive) as zipped:
            assert required <= set(zipped.namelist())

    print("P67 probe package scaffold test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
