#!/usr/bin/env python3
"""Generate the app icon, launch color is JSON, and the success chime."""

from __future__ import annotations

import math
import struct
import wave
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "PythonCoach" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png"
WAV = ROOT / "PythonCoach" / "Resources" / "SuccessChime.wav"


def chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, pixel) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixel(x, y))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def icon_pixel(x: int, y: int):
    width = 1024
    t = y / (width - 1)
    top = (36, 78, 220)
    bottom = (14, 150, 150)
    base = blend(top, bottom, t)
    # Soft inner card.
    left, top_y, size = 180, 250, 664
    radius = 72
    if left <= x < left + size and top_y <= y < top_y + size:
        dx = 0
        dy = 0
        if x < left + radius and y < top_y + radius:
            dx, dy = left + radius - x, top_y + radius - y
        elif x >= left + size - radius and y < top_y + radius:
            dx, dy = x - (left + size - radius - 1), top_y + radius - y
        elif x < left + radius and y >= top_y + size - radius:
            dx, dy = left + radius - x, y - (top_y + size - radius - 1)
        elif x >= left + size - radius and y >= top_y + size - radius:
            dx, dy = x - (left + size - radius - 1), y - (top_y + size - radius - 1)
        if dx * dx + dy * dy <= radius * radius or (dx == 0 and dy == 0):
            base = (246, 249, 255)
    # Prompt chevron.
    def chevron(px, py):
        # Two thick strokes forming >
        arm = abs((py - 560) * 0.72)
        return 300 <= px <= 470 and abs(px - 300 - arm) <= 28 and 400 <= py <= 720

    if chevron(x, y):
        base = (37, 86, 230)
    # Cursor block.
    if 520 <= x <= 690 and 640 <= y <= 700:
        base = (18, 168, 140)
    return base


def write_chime(path: Path) -> None:
    rate = 22050
    duration = 0.42

    def envelope(t, start, length):
        if t < start or t > start + length:
            return 0.0
        u = (t - start) / length
        return (u ** 0.18) * math.exp(-4.4 * u)

    frames = bytearray()
    total = int(rate * duration)
    for i in range(total):
        t = i / rate
        sample = 0.0
        sample += 0.55 * math.sin(2 * math.pi * 880 * t) * envelope(t, 0.0, 0.30)
        sample += 0.42 * math.sin(2 * math.pi * 1318.51 * t) * envelope(t, 0.08, 0.32)
        sample += 0.16 * math.sin(2 * math.pi * 1760 * t) * envelope(t, 0.08, 0.20)
        sample = max(-1.0, min(1.0, sample))
        frames += struct.pack("<h", int(sample * 32767 * 0.62))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(frames)


def main() -> None:
    write_png(ICON, 1024, 1024, icon_pixel)
    write_chime(WAV)
    print(f"icon={ICON.stat().st_size} wav={WAV.stat().st_size}")


if __name__ == "__main__":
    main()
