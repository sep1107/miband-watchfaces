#!/usr/bin/env python3
from __future__ import annotations

from p67_image_codec import (
    COMPRESSED_IMAGE_MAGIC,
    decode_rle,
    encode_rle,
    pack_compressed,
    unpack_compressed,
    pack_image_record,
    unpack_image_record,
    pack_image_array_record,
    unpack_image_array_record,
)


def make_palette() -> bytes:
    palette = bytearray(1024)
    palette[0:4] = bytes((0, 0, 0, 0))
    palette[4:8] = bytes((255, 0, 0, 255))
    palette[8:12] = bytes((0, 255, 0, 128))
    return bytes(palette)


def main() -> int:
    source = bytes(range(127)) + b"A" * 127 + bytes(range(127)) + b"Z" * 2
    encoded = encode_rle(source)
    assert decode_rle(encoded, len(source)) == source
    assert any(byte & 0x80 for byte in encoded)

    packed = pack_compressed(source, 1)
    assert int.from_bytes(packed[:4], "little") == COMPRESSED_IMAGE_MAGIC
    unpacked, unit_size = unpack_compressed(packed)
    assert unit_size == 1
    assert unpacked == source

    width, height = 4, 3
    palette = make_palette()
    first = bytes((0, 1, 1, 0, 2, 2, 2, 0, 1, 0, 2, 1))
    second = bytes(reversed(first))

    record = pack_image_record(width, height, palette, first)
    decoded = unpack_image_record(record)
    assert decoded["format"] == 16
    assert decoded["flags"] == 4
    assert decoded["width"] == width
    assert decoded["height"] == height
    assert decoded["palette"] == palette
    assert decoded["indices"] == first
    descriptor = int.from_bytes(record[16:20], "little")
    assert descriptor == ((1024 + width * height) << 4) | 1

    array = pack_image_array_record(
        width, height, [(palette, first), (palette, second)]
    )
    decoded_array = unpack_image_array_record(array)
    assert decoded_array["count"] == 2
    assert decoded_array["flags"] == 4
    assert decoded_array["images"][0]["indices"] == first
    assert decoded_array["images"][1]["indices"] == second
    assert sum(decoded_array["lengths"]) == decoded_array["payloadSize"]

    print("P67 indexed8 image codec round-trip passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
