#!/usr/bin/env python3
"""Build and inspect Xiaomi P67 watchface upload payloads.

This module prepares the data-channel envelope used after a watchface install
announcement has been accepted by the band. It does not open Bluetooth or send
commands; transport-specific code must deliver the returned chunks in order.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

WATCHFACE_MAGIC = 0x1234A55A
WATCHFACE_ID_OFFSET = 0x28
WATCHFACE_NAME_OFFSET = 0x68
WATCHFACE_UPLOAD_TYPE = 16
UPLOAD_PREFIX_SIZE = 2 + 16 + 4
UPLOAD_CRC_SIZE = 4
CHUNK_PREFIX_SIZE = 4


class TransferFormatError(ValueError):
    """Raised when a watchface or upload payload is structurally invalid."""


def _nul_text(data: bytes, offset: int, *, encoding: str = "utf-8") -> str | None:
    if offset < 0 or offset >= len(data):
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


def inspect_watchface(data: bytes) -> dict[str, object]:
    """Validate the raw P67 binary and return its embedded identity."""
    if len(data) <= WATCHFACE_NAME_OFFSET:
        raise TransferFormatError("watchface is too short for the P67 header")
    magic = struct.unpack_from("<I", data, 0)[0]
    if magic != WATCHFACE_MAGIC:
        raise TransferFormatError(f"unexpected watchface magic 0x{magic:08X}")
    package_id = _nul_text(data, WATCHFACE_ID_OFFSET, encoding="ascii")
    if not package_id or not package_id.isdigit():
        raise TransferFormatError("watchface package ID is missing or non-numeric")
    name = _nul_text(data, WATCHFACE_NAME_OFFSET) or package_id
    return {
        "magic": f"0x{magic:08X}",
        "packageId": package_id,
        "name": name,
        "size": len(data),
        "md5": hashlib.md5(data).hexdigest(),
    }


def build_upload_payload(
    file_bytes: bytes,
    *,
    upload_type: int = WATCHFACE_UPLOAD_TYPE,
    resume_position: int = 0,
) -> bytes:
    """Return envelope plus little-endian CRC32 for Xiaomi's data channel."""
    if not 0 <= upload_type <= 0xFF:
        raise ValueError("upload_type must fit in one byte")
    if not 0 <= resume_position <= len(file_bytes):
        raise ValueError("resume_position is outside the file")
    digest = hashlib.md5(file_bytes).digest()
    envelope = (
        bytes((0, upload_type))
        + digest
        + struct.pack("<I", len(file_bytes))
        + file_bytes[resume_position:]
    )
    return envelope + struct.pack("<I", zlib.crc32(envelope) & 0xFFFFFFFF)


def inspect_upload_payload(payload: bytes) -> dict[str, object]:
    """Inspect a non-resumed upload payload and verify its checksums."""
    minimum = UPLOAD_PREFIX_SIZE + UPLOAD_CRC_SIZE
    if len(payload) < minimum:
        raise TransferFormatError("upload payload is too short")
    envelope, crc_bytes = payload[:-4], payload[-4:]
    expected_crc = struct.unpack("<I", crc_bytes)[0]
    actual_crc = zlib.crc32(envelope) & 0xFFFFFFFF
    if actual_crc != expected_crc:
        raise TransferFormatError(
            f"CRC32 mismatch: got 0x{expected_crc:08X}, expected 0x{actual_crc:08X}"
        )
    if envelope[0] != 0:
        raise TransferFormatError("unexpected upload envelope marker")
    upload_type = envelope[1]
    digest = envelope[2:18]
    declared_size = struct.unpack_from("<I", envelope, 18)[0]
    file_bytes = envelope[22:]
    if len(file_bytes) != declared_size:
        raise TransferFormatError(
            "payload appears resumed or truncated; full-file inspection requires resume 0"
        )
    actual_md5 = hashlib.md5(file_bytes).digest()
    if actual_md5 != digest:
        raise TransferFormatError("file MD5 does not match the envelope")
    return {
        "uploadType": upload_type,
        "declaredSize": declared_size,
        "md5": digest.hex(),
        "crc32": f"0x{actual_crc:08X}",
        "fileBytes": file_bytes,
    }


def split_upload_chunks(payload: bytes, chunk_size: int) -> list[bytes]:
    """Split a payload into 1-based Xiaomi data-channel chunks."""
    if chunk_size <= CHUNK_PREFIX_SIZE:
        raise ValueError("chunk_size must be greater than four bytes")
    part_size = chunk_size - CHUNK_PREFIX_SIZE
    total = (len(payload) + part_size - 1) // part_size
    if total == 0:
        total = 1
    if total > 0xFFFF:
        raise ValueError("upload requires more than 65535 chunks")
    chunks: list[bytes] = []
    for index in range(total):
        start = index * part_size
        end = min(start + part_size, len(payload))
        chunks.append(struct.pack("<HH", total, index + 1) + payload[start:end])
    return chunks


def reassemble_upload_chunks(chunks: list[bytes]) -> bytes:
    if not chunks:
        raise TransferFormatError("no chunks supplied")
    expected_total = len(chunks)
    output = bytearray()
    for expected_index, chunk in enumerate(chunks, start=1):
        if len(chunk) < CHUNK_PREFIX_SIZE:
            raise TransferFormatError(f"chunk {expected_index} is too short")
        total, index = struct.unpack_from("<HH", chunk, 0)
        if total != expected_total or index != expected_index:
            raise TransferFormatError(
                f"chunk header mismatch at {expected_index}: total={total}, index={index}"
            )
        output.extend(chunk[CHUNK_PREFIX_SIZE:])
    return bytes(output)


def build_plan(file_bytes: bytes, chunk_size: int = 2048) -> dict[str, object]:
    identity = inspect_watchface(file_bytes)
    payload = build_upload_payload(file_bytes)
    chunks = split_upload_chunks(payload, chunk_size)
    return {
        "watchface": identity,
        "protocol": {
            "watchfaceCommandType": 4,
            "watchfaceInstallSubtype": 4,
            "dataUploadCommandType": 22,
            "dataUploadSubtype": 0,
            "uploadType": WATCHFACE_UPLOAD_TYPE,
            "chunkSize": chunk_size,
            "partPayloadSize": chunk_size - CHUNK_PREFIX_SIZE,
            "chunkCount": len(chunks),
            "uploadPayloadSize": len(payload),
        },
        "payload": payload,
        "chunks": chunks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_bin", type=Path)
    parser.add_argument("--chunk-size", type=int, default=2048)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    file_bytes = args.resource_bin.read_bytes()
    plan = build_plan(file_bytes, args.chunk_size)
    report = {"watchface": plan["watchface"], "protocol": plan["protocol"]}
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "upload-payload.bin").write_bytes(plan["payload"])
        for index, chunk in enumerate(plan["chunks"], start=1):
            (args.out_dir / f"chunk-{index:05d}.bin").write_bytes(chunk)
        (args.out_dir / "upload-plan.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
