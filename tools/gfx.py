"""gfx.py: read, render and rewrite 4/8-bpp TIM images inside disc files (graphics-text redraws, phase 8).

    python -X utf8 tools/gfx.py render FILE OFF OUT.png [--zoom N] [--clut K]   # FILE under work/disc/tree
Library: Tim(data, off) -> .w .h .bpp .clut (list of 15-bit colours) .get(x, y) / .set(x, y, idx) / .bytes();
rgb(c15) -> (r, g, b). Offsets are of the TIM header (magic 0x10). Generators (tools/gfx_*.py) draw with palette
indices only, so a re-import never needs colour matching.
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work/disc/tree"


def rgb(c):
    return ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)


class Tim:
    def __init__(self, data, off):
        assert data[off:off + 4] == b"\x10\x00\x00\x00", f"no TIM at {off:#x}"
        flags = struct.unpack_from("<I", data, off + 4)[0]
        self.bpp = (4, 8, 16, 24)[flags & 3]
        assert self.bpp in (4, 8) and flags & 8, "only CLUT images"
        p = off + 8
        blen, _, _, cw, ch = struct.unpack_from("<IHHHH", data, p)
        self.clut = list(struct.unpack_from(f"<{cw * ch}H", data, p + 12))
        self.ncol = cw
        p += blen
        blen, _, _, ww, self.h = struct.unpack_from("<IHHHH", data, p)
        self.w = ww * 16 // self.bpp
        self.off, self.px_off, self.px = off, p + 12, bytearray(data[p + 12:p + blen])

    def get(self, x, y):
        if self.bpp == 8:
            return self.px[y * self.w + x]
        return (self.px[(y * self.w + x) // 2] >> (4 * (x & 1))) & 15

    def set(self, x, y, i):
        if self.bpp == 8:
            self.px[y * self.w + x] = i
            return
        k, s = (y * self.w + x) // 2, 4 * (x & 1)
        self.px[k] = (self.px[k] & ~(15 << s) & 0xFF) | (i << s)

    def image(self, clut=0):
        pal = [rgb(c) for c in self.clut[clut * self.ncol:(clut + 1) * self.ncol]]
        img = Image.new("RGB", (self.w, self.h))
        img.putdata([pal[self.get(x, y)] if self.get(x, y) < len(pal) else (255, 0, 255)
                     for y in range(self.h) for x in range(self.w)])
        return img

    def write(self, data):
        """Pixels back into `data` (bytearray), same place and size."""
        data[self.px_off:self.px_off + len(self.px)] = self.px


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("file")
    r.add_argument("off", type=lambda s: int(s, 16))
    r.add_argument("out")
    r.add_argument("--zoom", type=int, default=1)
    r.add_argument("--clut", type=int, default=0)
    a = ap.parse_args()
    path = Path(a.file) if Path(a.file).exists() else TREE / a.file
    t = Tim(path.read_bytes(), a.off)
    img = t.image(a.clut)
    img.resize((t.w * a.zoom, t.h * a.zoom), Image.NEAREST).save(a.out)
    print(f"{t.bpp} bpp {t.w}x{t.h}, {len(t.clut)} clut colours ({t.ncol} per row) -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
