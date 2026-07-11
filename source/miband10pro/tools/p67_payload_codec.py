#!/usr/bin/env python3
"""P67 payload codecs for layout, data, slot, and widget records."""
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
            raise PayloadError(f"layout payload must be 16