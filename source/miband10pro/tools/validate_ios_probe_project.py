#!/usr/bin/env python3
"""Validate the generated iPhone probe scaffold and its read-only boundary."""
from __future__ import annotations

import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "ios-probe"

REQUIRED_FILES = [
    "P67ProbeApp.swift",
    "P67ReadOnlyProbe.swift",
    "P67ReadOnlyProbeView.swift",
    "Info.plist",
    "project.yml",
    "generate_project.sh",
]

FORBIDDEN_SWIFT_TOKENS = [
    ".writeValue(",
    ".setNotifyValue(",
    "sendEncryptedCommand",
    "watchfaceInstall",
    "DataUploadService",
    "deleteWatchface",
    "AuthKeyStore",
    "requestUpload(",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    for relative in REQUIRED_FILES:
        require((ROOT / relative).is_file(), f"missing iPhone probe file: {relative}")

    project = (ROOT / "project.yml").read_text(encoding="utf-8")
    for token in [
        "platform: iOS",
        'deploymentTarget: "17.0"',
        "P67ProbeApp.swift",
        "P67ReadOnlyProbe.swift",
        "P67ReadOnlyProbeView.swift",
        "SWIFT_VERSION: 5.9",
        "com.sep1107.p67-read-only-probe",
    ]:
        require(token in project, f"project.yml is missing: {token}")

    plist = plistlib.loads((ROOT / "Info.plist").read_bytes())
    description = plist.get("NSBluetoothAlwaysUsageDescription", "")
    require("without writing" in description, "Bluetooth permission must state read-only intent")
    require("UIBackgroundModes" not in plist, "read-only probe must not request background Bluetooth")

    swift_files = sorted(ROOT.glob("*.swift"))
    require(len(swift_files) == 3, "unexpected Swift source count in iPhone probe")
    swift = "\n".join(path.read_text(encoding="utf-8") for path in swift_files)

    for token in FORBIDDEN_SWIFT_TOKENS:
        require(token not in swift, f"iPhone probe contains forbidden write/upload API: {token}")

    for token in [
        "@main",
        "P67ReadOnlyProbeView()",
        'hasPrefix("Xiaomi Smart Band 10 Pro")',
        "0000FE95",
        "0000005E",
        "0000005F",
        "discoverServices",
        "discoverCharacteristics",
    ]:
        require(token in swift, f"iPhone probe is missing required discovery token: {token}")

    script = (ROOT / "generate_project.sh").read_text(encoding="utf-8")
    require("xcodegen generate --spec project.yml" in script, "project generator command changed")

    print("P67 iPhone read-only Xcode project scaffold passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
