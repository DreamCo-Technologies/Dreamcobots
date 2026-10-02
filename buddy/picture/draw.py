#!/usr/bin/env python3
"""Draw a picture with Buddy's own code. No Stable Diffusion and no download."""
from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path

import numpy as np


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, rgb: np.ndarray) -> None:
    height, width, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[row].astype(np.uint8).tobytes() for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(raw)) + _chunk(b"IEND", b""))


def tint(path: Path) -> tuple[int, int, int]:
    digest = hashlib.sha256(path.read_bytes()).digest()
    return digest[0], digest[1], digest[2]


def draw(prompt: str, reference: Path, output: Path) -> Path:
    """Make a small original picture. This does not reproduce a person's face."""
    color = tint(reference)
    picture = np.zeros((64, 96, 3), dtype=np.uint8)
    picture[:] = color
    for index, char in enumerate(prompt[:24].lower()):
        column = 4 + (index % 12) * 7
        row = 16 + (index // 12) * 20
        shade = (ord(char) * 13) % 180
        picture[row:row + 8, column:column + 5] = (255 - shade, shade, 180)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_png(output, picture)
    return output
