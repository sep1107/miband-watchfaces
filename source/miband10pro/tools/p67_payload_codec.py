#!/usr/bin/env python3
"""P67 payload codecs for layout, data, slot, and widget records.

The codecs preserve unknown bytes where the real P67 package carries fields not
fully named yet. All integers are little-endian.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import struct


class PayloadError(ValueError):
    pass


def _need(data: bytes, size: int, label: str) -> None:
    if len(data) < size:
        raise PayloadError(f"{label} needs at least {size} bytes, got {len(data)}")


@dataclass(eq=True)
class LayoutPayload:
    resource_uid: int
    x: int
    y: int
    parameter: int = 0
    reserved1: int = 0
    reserved2: int = 0

    SIZE = 16

    @classmethod
    def decode(cls, data: bytes) -> "LayoutPayload":
        if len(data) != cls.SIZE:
            raise PayloadError(f"layout payload must be 16 bytes, got {len(data)}")
        return cls(*struct.unpack("<IHHIHH", data))

    def encode(self) -> bytes:
        return struct.pack(
            "<IHHIHH",
            self.resource_uid,
            self.x,
            self.y,
            self.parameter,
            self.reserved1,
            self.reserved2,
        )


@dataclass(eq=True)
class DataCommon:
    source_id: int
    digits: int
    flags: int
    flags1: int
    parameter: int

    SIZE = 8

    @property
    def style(self) -> int:
        return (self.flags >> 4) & 0x0F

    @classmethod
    def decode(cls, data: bytes) -> "DataCommon":
        _need(data, cls.SIZE, "data common header")
        return cls(*struct.unpack_from("<HBBHH", data, 0))

    def encode(self) -> bytes:
        return struct.pack(
            "<HBBHH",
            self.source_id,
            self.digits,
            self.flags,
            self.flags1,
            self.parameter,
        )


@dataclass(eq=True)
class ImageNumberStyle:
    image_array