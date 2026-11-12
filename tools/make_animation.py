#!/usr/bin/env python3
"""Convert a GIF (or a folder of images) into the animation.bin played by the firmware.

Author: DeadPohl  https://www.instagram.com/_deadpohl_

Examples:
    python make_animation.py my.gif
    python make_animation.py my.gif --fps 20 --quality 80
    python make_animation.py ../firmware/assets/hamster          # folder of frames
    python make_animation.py --verify ../firmware/assets/animation.bin

Every frame is cropped to a square, resized to the display size and stored as a
baseline JPEG, together with its display time. The result is embedded in the
firmware, so there is no filesystem to upload.

File format (little endian):
    header   4s magic "HWA1", u16 frame count, u16 width, u16 height, u16 reserved
    table    per frame: u32 offset, u32 size, u16 delay in ms, u16 reserved
    data     the JPEG files, back to back
"""
import argparse
import io
import re
import struct
import sys
from pathlib import Path

from PIL import Image, ImageSequence

MAGIC = b"HWA1"
HEADER = struct.Struct("<4sHHHH")
ENTRY = struct.Struct("<IIHH")
SIZE = 240
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
# Firmware uses the huge_app partition (3 MB). Keep room for the program itself.
MAX_BYTES = 2_000_000


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def load_frames(src):
    """Return a list of (PIL RGB image, delay in ms or None)."""
    src = Path(src)
    if src.is_dir():
        files = sorted((f for f in src.iterdir() if f.suffix.lower() in IMAGE_EXT), key=natural_key)
        if not files:
            sys.exit(f"No images found in {src}")
        return [(Image.open(f).convert("RGB"), None) for f in files]
    img = Image.open(src)
    frames = []
    for fr in ImageSequence.Iterator(img):
        frames.append((fr.convert("RGB"), fr.info.get("duration")))
    return frames


def square(im, size=SIZE):
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    return im.resize((size, size), Image.LANCZOS)


def build(frames, fps, quality, step):
    blobs, delays = [], []
    for i, (im, dur) in enumerate(frames):
        if i % step:
            continue
        buf = io.BytesIO()
        # baseline JPEG, 4:2:0: what the on-device decoder handles fastest
        square(im).save(buf, "JPEG", quality=quality, subsampling=2, progressive=False, optimize=False)
        blobs.append(buf.getvalue())
        if fps:
            delays.append(round(1000 / fps))
        else:
            delays.append(max(20, (dur or 40) * step))
    n = len(blobs)
    offset = HEADER.size + ENTRY.size * n
    out = bytearray(HEADER.pack(MAGIC, n, SIZE, SIZE, 0))
    for b, d in zip(blobs, delays):
        out += ENTRY.pack(offset, len(b), d, 0)
        offset += len(b)
    for b in blobs:
        out += b
    return bytes(out)


def verify(path):
    data = Path(path).read_bytes()
    magic, n, w, h, _ = HEADER.unpack_from(data, 0)
    assert magic == MAGIC, "bad magic"
    total_ms = 0
    for i in range(n):
        off, size, delay, _ = ENTRY.unpack_from(data, HEADER.size + ENTRY.size * i)
        im = Image.open(io.BytesIO(data[off:off + size]))
        im.load()
        assert im.size == (w, h), f"frame {i} has size {im.size}"
        assert im.format == "JPEG" and "progressive" not in im.info, f"frame {i} is not baseline JPEG"
        total_ms += delay
    print(f"OK: {n} frames of {w}x{h}, {len(data) / 1024:.0f} KB, loop {total_ms / 1000:.2f} s "
          f"({1000 * n / total_ms:.1f} fps)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", help="GIF file or folder of images")
    ap.add_argument("-o", "--out", default=str(Path(__file__).resolve().parent.parent / "firmware" / "assets" / "animation.bin"))
    ap.add_argument("--fps", type=float, help="fixed frame rate (default: use the GIF delays, 25 fps for a folder)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG quality 1-95 (default 85)")
    ap.add_argument("--step", type=int, default=1, help="keep one frame out of N (shrinks the file)")
    ap.add_argument("--reverse", action="store_true", help="play the frames backwards")
    ap.add_argument("--verify", metavar="BIN", help="check an existing animation.bin and exit")
    a = ap.parse_args()

    if a.verify:
        verify(a.verify)
        return
    if not a.source:
        ap.error("source is required")
    frames = load_frames(a.source)
    if a.reverse:
        frames.reverse()
    fps = a.fps or (25.0 if all(d is None for _, d in frames) else None)
    data = build(frames, fps, a.quality, a.step)
    if len(data) > MAX_BYTES:
        sys.exit(f"{len(data) / 1e6:.2f} MB is too big (limit {MAX_BYTES / 1e6:.1f} MB). "
                 "Lower --quality, use --step 2, or give fewer frames.")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"Wrote {out}")
    verify(out)


if __name__ == "__main__":
    main()
