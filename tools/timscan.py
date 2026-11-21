"""timscan.py: find PS1 TIM images in disc files and render them to labelled contact sheets (graphics-text survey).

    python -X utf8 tools/timscan.py OUTDIR FILE.. [--min 16]
Writes OUTDIR/<file>_<n>.png sheets (each tile labelled hex offset, bpp, size) and OUTDIR/index.tsv
(file, offset, bpp, w, h, clut count, bytes). Prints every skipped candidate and why. Needs Pillow.
4/8 bpp use the first CLUT row; 16 bpp is direct colour."""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def c15(v):
    return ((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3)


def parse(d, off):
    """Return (bpp, w, h, clut, pixels_bytes, total_len) or raise ValueError."""
    if d[off:off + 4] != b"\x10\x00\x00\x00":
        raise ValueError("magic")
    flags = struct.unpack_from("<I", d, off + 4)[0]
    if flags & ~0xB:
        raise ValueError("flags")
    mode = flags & 3
    p = off + 8
    clut = []
    if flags & 8:
        blen, _x, _y, cw, ch = struct.unpack_from("<IHHHH", d, p)
        if blen != 12 + cw * ch * 2 or cw == 0 or ch == 0 or p + blen > len(d):
            raise ValueError("clut")
        clut = list(struct.unpack_from("<%dH" % (cw * ch), d, p + 12))
        p += blen
    elif mode in (0, 1):
        raise ValueError("no clut")
    blen, _x, _y, ww, h = struct.unpack_from("<IHHHH", d, p)
    if blen != 12 + ww * h * 2 or ww == 0 or h == 0 or ww > 1024 or h > 512 or p + blen > len(d):
        raise ValueError("image")
    bpp = (4, 8, 16, 24)[mode]
    w = ww * 16 // bpp
    return bpp, w, h, clut, d[p + 12:p + blen], p + blen - off


def render(bpp, w, h, clut, px):
    img = Image.new("RGB", (w, h))
    put = img.load()
    for y in range(h):
        for x in range(w):
            if bpp == 4:
                b = px[(y * w + x) // 2]
                i = (b >> (4 * (x & 1))) & 15
                put[x, y] = c15(clut[i]) if i < len(clut) else (255, 0, 255)
            elif bpp == 8:
                i = px[y * w + x]
                put[x, y] = c15(clut[i]) if i < len(clut) else (255, 0, 255)
            elif bpp == 16:
                put[x, y] = c15(struct.unpack_from("<H", px, (y * w + x) * 2)[0])
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--min", type=int, default=16, help="skip images smaller than this in both dimensions")
    ap.add_argument("--sheet-w", type=int, default=1024)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    idx = open(out / "index.tsv", "w", encoding="utf-8")
    idx.write("file\toffset\tbpp\tw\th\tcluts\tbytes\n")
    for fn in a.files:
        d = Path(fn).read_bytes()
        tims = []
        off = d.find(b"\x10\x00\x00\x00")
        while off >= 0:
            try:
                bpp, w, h, clut, px, n = parse(d, off)
            except (ValueError, struct.error):
                off = d.find(b"\x10\x00\x00\x00", off + 1)
                continue
            if bpp == 24:
                print(f"skip {fn}+{off:#x}: 24bpp not rendered")
            elif w < a.min and h < a.min:
                print(f"skip {fn}+{off:#x}: {w}x{h} below --min")
            else:
                tims.append((off, bpp, w, h, clut, px))
            idx.write(f"{fn}\t{off:#x}\t{bpp}\t{w}\t{h}\t{len(clut) // 16 if clut else 0}\t{n}\n")
            off = d.find(b"\x10\x00\x00\x00", off + n)
        stem = Path(fn).name.replace(".", "_")
        page, x, y, rowh, n = None, 0, 0, 0, 0
        pages = []
        for off, bpp, w, h, clut, px in tims:
            img = render(bpp, w, h, clut, px)
            if img.width > a.sheet_w:
                img = img.resize((a.sheet_w, img.height * a.sheet_w // img.width))
            if page is None or x + img.width > a.sheet_w:
                x, y, rowh = 0, y + rowh + 12, 0
            if page is None or y + img.height + 12 > 1024:
                page = Image.new("RGB", (a.sheet_w, 1024), (40, 0, 40))
                pages.append(page)
                x, y, rowh = 0, 0, 0
            page.paste(img, (x, y + 12))
            ImageDraw.Draw(page).text((x + 1, y), f"{off:x} {bpp}b {w}x{h}", fill=(255, 255, 0))
            x += img.width + 4
            rowh = max(rowh, img.height)
            n += 1
        for i, pg in enumerate(pages):
            pg.save(out / f"{stem}_{i:02d}.png")
        print(f"{fn}: {n} TIMs, {len(pages)} sheets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
