#!/usr/bin/env python3
"""Encode and decode P67 indexed8 image payloads and image records."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

COMPRESSED_IMAGE_MAGIC = 0x5AA521E0
IMAGE_FORMAT_INDEXED8_RLE = 16
IMAGE_COMPRESSION_FLAG = 0x04
PALETTE_SIZE = 256 * 4
MAX_RUN = 0x7F


def _units(data: bytes, unit_size: int) -> list[bytes]:
    if unit_size <= 0:
        raise ValueError("unit_size must be positive")
    if len(data) % unit_size:
        raise ValueError("data length must be divisible by unit_size")
    return [data[i : i + unit_size] for i in range(0, len(data), unit_size)]


def encode_rle(data: bytes, unit_size: int = 1) -> bytes:
    """Encode units with P67's reversed PackBits convention.

    Control byte bit 7 set: copy N literal units.
    Control byte bit 7 clear: repeat the following unit N times.
    N is stored in bits 0..6 and ranges from 1 to 127.
    """

    source = _units(data, unit_size)
    out = bytearray()
    i = 0

    while i < len(source):
        run = 1
        while (
            i + run < len(source)
            and run < MAX_RUN
            and source[i + run] == source[i]
        ):
            run += 1

        if run >= 2:
            out.append(run)
            out.extend(source[i])
            i += run
            continue

        literal_start = i
        i += 1
        while i < len(source) and i - literal_start < MAX_RUN:
            next_run = 1
            while (
                i + next_run < len(source)
                and next_run < MAX_RUN
                and source[i + next_run] == source[i]
            ):
                next_run += 1
            if next_run >= 2:
                break
            i += 1

        count = i - literal_start
        out.append(0x80 | count)
        for unit in source[literal_start:i]:
            out.extend(unit)

    return bytes(out)


def decode_rle(encoded: bytes, expected_size: int, unit_size: int = 1) -> bytes:
    if expected_size < 0:
        raise ValueError("expected_size cannot be negative")
    if expected_size % unit_size:
        raise ValueError("expected_size must be divisible by unit_size")

    out = bytearray()
    cursor = 0
    while cursor < len(encoded) and len(out) < expected_size:
        control = encoded[cursor]
        cursor += 1
        count = control & MAX_RUN
        if count == 0:
            raise ValueError("zero-length RLE command")

        if control & 0x80:
            size = count * unit_size
            end = cursor + size
            if end > len(encoded):
                raise ValueError("truncated literal RLE command")
            out.extend(encoded[cursor:end])
            cursor = end
        else:
            end = cursor + unit_size
            if end > len(encoded):
                raise ValueError("truncated repeat RLE command")
            out.extend(encoded[cursor:end] * count)
            cursor = end

        if len(out) > expected_size:
            raise ValueError("RLE stream expands beyond declared size")

    if len(out) != expected_size:
        raise ValueError(
            f"RLE size mismatch: decoded {len(out)}, expected {expected_size}"
        )
    if cursor != len(encoded):
        raise ValueError(f"unused compressed bytes: {len(encoded) - cursor}")
    return bytes(out)


def pack_compressed(raw: bytes, bytes_per_unit: int = 1) -> bytes:
    if not 1 <= bytes_per_unit <= 0x0F:
        raise ValueError("bytes_per_unit must fit in four bits")
    descriptor = (len(raw) << 4) | bytes_per_unit
    return struct.pack("<II", COMPRESSED_IMAGE_MAGIC, descriptor) + encode_rle(
        raw, bytes_per_unit
    )


def unpack_compressed(payload: bytes) -> tuple[bytes, int]:
    if len(payload) < 8:
        raise ValueError("compressed payload is shorter than eight bytes")
    magic, descriptor = struct.unpack_from("<II", payload, 0)
    if magic != COMPRESSED_IMAGE_MAGIC:
        raise ValueError(f"unexpected image magic: 0x{magic:08X}")
    bytes_per_unit = descriptor & 0x0F
    raw_size = descriptor >> 4
    if bytes_per_unit == 0:
        raise ValueError("compressed payload declares a zero-sized unit")
    return decode_rle(payload[8:], raw_size, bytes_per_unit), bytes_per_unit


def pack_indexed8(palette_rgba: bytes, indices: bytes) -> bytes:
    if len(palette_rgba) != PALETTE_SIZE:
        raise ValueError(f"indexed8 palette must contain {PALETTE_SIZE} bytes")
    return pack_compressed(palette_rgba + indices, 1)


def unpack_indexed8(payload: bytes, width: int, height: int) -> tuple[bytes, bytes]:
    raw, bytes_per_unit = unpack_compressed(payload)
    if bytes_per_unit != 1:
        raise ValueError(f"indexed8 payload uses {bytes_per_unit} bytes per unit")
    expected = PALETTE_SIZE + width * height
    if len(raw) != expected:
        raise ValueError(f"indexed8 raw size is {len(raw)}, expected {expected}")
    return raw[:PALETTE_SIZE], raw[PALETTE_SIZE:]


def pack_image_record(width: int, height: int, palette_rgba: bytes, indices: bytes) -> bytes:
    if len(indices) != width * height:
        raise ValueError("index count does not match image dimensions")
    payload = pack_indexed8(palette_rgba, indices)
    header = struct.pack(
        "<BBHHHI",
        IMAGE_FORMAT_INDEXED8_RLE,
        IMAGE_COMPRESSION_FLAG,
        0,
        width,
        height,
        len(payload),
    )
    return header + payload


def unpack_image_record(record: bytes) -> dict:
    if len(record) < 12:
        raise ValueError("image record is shorter than twelve bytes")
    fmt, flags, reserved, width, height, payload_size = struct.unpack_from(
        "<BBHHHI", record, 0
    )
    if len(record) != 12 + payload_size:
        raise ValueError("image record length does not match payload size")
    palette, indices = unpack_indexed8(record[12:], width, height)
    return {
        "format": fmt,
        "flags": flags,
        "reserved": reserved,
        "width": width,
        "height": height,
        "payloadSize": payload_size,
        "palette": palette,
        "indices": indices,
    }


def pack_image_array_record(
    width: int, height: int, indexed_images: list[tuple[bytes, bytes]]
) -> bytes:
    if not indexed_images or len(indexed_images) > 255:
        raise ValueError("image array count must be between 1 and 255")
    payloads = []
    for palette, indices in indexed_images:
        if len(indices) != width * height:
            raise ValueError("array image index count does not match dimensions")
        payloads.append(pack_indexed8(palette, indices))
    header = struct.pack(
        "<BBHHHI",
        IMAGE_FORMAT_INDEXED8_RLE,
        len(payloads),
        IMAGE_COMPRESSION_FLAG,
        width,
        height,
        sum(map(len, payloads)),
    )
    lengths = struct.pack("<" + "I" * len(payloads), *map(len, payloads))
    return header + lengths + b"".join(payloads)


def unpack_image_array_record(record: bytes) -> dict:
    if len(record) < 12:
        raise ValueError("image array record is shorter than twelve bytes")
    fmt, count, flags, width, height, payload_size = struct.unpack_from(
        "<BBHHHI", record, 0
    )
    table_end = 12 + count * 4
    if table_end > len(record):
        raise ValueError("truncated image array length table")
    lengths = list(struct.unpack_from("<" + "I" * count, record, 12))
    if sum(lengths) != payload_size:
        raise ValueError("image array payload size does not match item lengths")
    if len(record) != table_end + payload_size:
        raise ValueError("image array record length mismatch")

    images = []
    cursor = table_end
    for size in lengths:
        payload = record[cursor : cursor + size]
        palette, indices = unpack_indexed8(payload, width, height)
        images.append({"palette": palette, "indices": indices, "payloadSize": size})
        cursor += size
    return {
        "format": fmt,
        "count": count,
        "flags": flags,
        "width": width,
        "height": height,
        "payloadSize": payload_size,
        "lengths": lengths,
        "images": images,
    }


def _rgba_from_indexed(palette: bytes, indices: bytes) -> bytes:
    out = bytearray()
    for index in indices:
        start = index * 4
        out.extend(palette[start : start + 4])
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_bin", type=Path)
    parser.add_argument("offset", type=lambda value: int(value, 0))
    parser.add_argument("length", type=lambda value: int(value, 0))
    parser.add_argument("--array", action="store_true")
    parser.add_argument("--png", type=Path)
    args = parser.parse_args()

    data = args.resource_bin.read_bytes()
    end = args.offset + args.length
    if args.offset < 0 or end > len(data):
        raise SystemExit("record range is outside resource.bin")
    record = data[args.offset:end]
    decoded = (
        unpack_image_array_record(record) if args.array else unpack_image_record(record)
    )

    report = {
        key: value
        for key, value in decoded.items()
        if key not in {"palette", "indices", "images"}
    }
    if args.array:
        report["decodedImages"] = len(decoded["images"])
    print(json.dumps(report, indent=2))

    if args.png:
        if args.array:
            raise SystemExit("--png currently supports a single image record")
        try:
            from PIL import Image
        except ImportError as exc:
            raise SystemExit("Pillow is required for --png") from exc
        rgba = _rgba_from_indexed(decoded["palette"], decoded["indices"])
        image = Image.frombytes(
            "RGBA", (decoded["width"], decoded["height"]), rgba
        )
        args.png.parent.mkdir(parents=True, exist_ok=True)
        image.save(args.png)
        print(f"Wrote {args.png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
