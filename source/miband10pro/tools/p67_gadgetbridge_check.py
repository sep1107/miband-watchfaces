#!/usr/bin/env python3
"""Check whether a P67 resource.bin satisfies Gadgetbridge import rules."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

MAGIC_BYTES = b"\x5a\xa5"
ID_OFFSET = 0x28
NAME_OFFSET = 0x68
I18N_OFFSET_FIELD = 0x74
I18N_SIZE_FIELD = 0x78
PREVIEW_OFFSET_FIELD = 0x20
MAX_FILE_SIZE = 128 * 1024 * 1024


def _nul_text(data: bytes, offset: int, encoding: str = "utf-8") -> str | None:
    if offset < 0 or offset >= len(data):
        return None
    end = data.find(b"\0", offset)
   