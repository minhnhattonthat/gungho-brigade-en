"""Prologue history captions: 23 FACE.DAT stills (8bpp 320x240) with Japanese burned in at the bottom centre.

    python -X utf8 tools/gfx_captions.py OUT.png [--zoom 2]   # preview JP | EN caption strips (tools/insert.py applies it)

Each captioned still has a caption-free grey twin (DONOR, same picture, its own palette). The caption pixels (rows
180-239 that differ from the twin, grown by 2 px) get the twin's picture back, mapped to the still's own palette;
then the English is drawn in DejaVu Sans Bold (fonts/, Bitstream Vera licence) white with a dark 1-px outline like
the Japanese, centred on the Japanese caption. Colour stills (0x55c000) refill each caption pixel from the nearest
clean pixel whose twin grey matches, so the hue stays. Wording follows glossary.md; `|` breaks a line.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gfx import ROOT, TREE, Tim  # noqa: E402

FILE = "FACE.DAT"
FONT = ROOT / "fonts/DejaVuSans-Bold.ttf"
Y0 = 180  # captions sit in rows 186-232
# still offset, caption-free twin, English
CAPTIONS = [
    (0x23E000, 0x277000, "2220 AD: the terraforming of Mars is complete"),
    (0x251000, 0x277000, "Same year: the Mars Century calendar is adopted"),
    (0x28A000, 0x2C3000, "Mars Year 46: food exports begin|to the Outer Planets Autonomous Zone"),
    (0x29D000, 0x2C3000, 'Same year: work begins on|the orbital elevator "Artsutanov"'),
    (0x2D6000, 0x322000, "Year 81: the Outer Planets Autonomous Zone|secedes from the Earth Federation"),
    (0x2E9000, 0x322000, "Same year: the Outer Planets Union is founded"),
    (0x2FC000, 0x322000, "Year 100: the Union of Martian States|declares a Martian government"),
    (0x335000, 0x36E000, "Year 149: the Junk is discovered"),
    (0x348000, 0x36E000, "The Junk Rush begins"),
    (0x381000, 0x3BA000, "Year 150: Mars's population tops 1.5 million"),
    (0x394000, 0x3BA000, "Year 156: Lake Huygens is found underground"),
    (0x3CD000, 0x406000, 'Year 163: the Mars Civil War ("Water War")|breaks out. Earth\'s mediation fails.'),
    (0x3E0000, 0x406000, "Year 165: Earth Federation peace forces step in.|The northern states agree to a ceasefire."),
    (0x419000, 0x452000, 'Same year: "Junkie" machine legs are sighted,|and machine legs vanish, one after another.'),
    (0x42C000, 0x452000, 'Missing machine legs outnumber a full battalion|and become known as the "Lost Battalion."'),
    (0x465000, 0x4B1000, "Year 166: the Southern Confederation's 101st|Cavalry Brigade engages an unidentified unit."),
    (0x478000, 0x4B1000, "The brigade is wiped out.|The southern states agree to a ceasefire."),
    (0x48B000, 0x4B1000, "The Mars Civil War ends."),
    (0x4EA000, 0x4D7000, 'Year 104: "Artsutanov" is completed'),
    (0x4FD000, 0x4D7000, "Same year: the Mars Union becomes|independent of the Earth Federation"),
    (0x510000, 0x4D7000, 'Year 105: a 999-Earth-year lease|on "Artsutanov" is signed'),
    (0x549000, 0x536000, "Mars Year 168"),
    (0x55C000, 0x536000, "Mars Year 168"),
]
MASK_FROM = {0x55C000: 0x549000}  # colour still: its caption sits where the grey sibling's does (same picture)
SIZE, LEAD, MAXW = 11, 15, 304  # px font size, line pitch, widest line


def rgb(t):
    return np.array([[(c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3] for c in t.clut[:256]], float)


def pixels(t):
    return np.frombuffer(bytes(t.px), np.uint8).reshape(t.h, t.w)


def nearest(pal, colours):
    """Palette index nearest to each RGB row of `colours` (N x 3)."""
    return np.argmin(((colours[:, None, :] - pal[None]) ** 2).sum(2), 1).astype(np.uint8)


def caption_mask(still, donor):
    a, b = rgb(still)[pixels(still)].mean(2), rgb(donor)[pixels(donor)].mean(2)
    m = np.zeros(a.shape, bool)
    m[Y0:] = np.abs(a[Y0:] - b[Y0:]) > 24
    for _ in range(2):  # grow over the soft outline
        g = m.copy()
        g[1:] |= m[:-1]
        g[:-1] |= m[1:]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    return m


def text_layer(lines, cx, cy):
    """-> (alpha of the white fill, alpha of the dark outline + halo), 240x320 floats 0..1, centred on (cx, cy)."""
    font = ImageFont.truetype(str(FONT), SIZE)
    fill, edge, halo = (Image.new("L", (320, 240)) for _ in range(3))
    top = cy - LEAD * len(lines) / 2
    for k, ln in enumerate(lines):
        w = font.getlength(ln)
        assert w <= MAXW, f"caption line {ln!r} is {w:.0f} px, max {MAXW}"
        x, y = round(cx - w / 2), round(top + LEAD * k)
        ImageDraw.Draw(halo).text((x, y), ln, font=font, fill=255, stroke_width=2, stroke_fill=255)
        ImageDraw.Draw(edge).text((x, y), ln, font=font, fill=255, stroke_width=1, stroke_fill=255)
        ImageDraw.Draw(fill).text((x, y), ln, font=font, fill=255)
    a = lambda im: np.asarray(im, float) / 255  # noqa: E731
    return a(fill), np.maximum(a(edge), 0.6 * a(halo))


def redraw(data, off, donor_off, text):
    """`data`: the unpatched file (twins and masks read from it); -> the still's Tim with the English drawn."""
    t, d = Tim(data, off), Tim(data, donor_off)
    pal, px = rgb(t), pixels(t).copy()
    m = caption_mask(Tim(data, MASK_FROM.get(off, off)), d)
    ys, xs = np.nonzero(m)
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    img = pal[px]
    grey = rgb(d)[pixels(d)]
    if np.ptp(pal, axis=1).max() < 24:  # grey still: the twin's picture, in this palette
        img[m] = grey[m]
    else:  # colour still: nearest clean pixel with the twin's grey
        cy_, cx_ = np.nonzero(~m & (np.arange(240)[:, None] >= Y0 - 20))
        for y, x in zip(ys, xs):
            r = 6
            while not (near := (np.abs(cy_ - y) <= r) & (np.abs(cx_ - x) <= r)).any():
                r += 4
            k = np.argmin(np.abs(grey[cy_[near], cx_[near], 0] - grey[y, x, 0]))
            img[y, x] = img[cy_[near][k], cx_[near][k]]
    fill, edge = text_layer(text.split("|"), cx, cy)
    ink = np.maximum(fill, edge)[..., None]
    shade = np.where(fill[..., None] > 0, 255.0, 24.0)
    img = img * (1 - ink) + shade * ink
    touched = m | (ink[..., 0] > 0)
    px[touched] = nearest(pal, img[touched])
    t.px[:] = px.tobytes()
    return t


def patch(data):
    out = bytearray(data)
    for off, donor, text in CAPTIONS:
        redraw(data, off, donor, text).write(out)
    return bytes(out)


def ranges(name):
    """Byte ranges of `name` this patch may change (tools/diffcheck.py)."""
    if name != FILE:
        return []
    data = (TREE / FILE).read_bytes()
    return [(t.px_off, t.px_off + len(t.px)) for t in (Tim(data, off) for off, _, _ in CAPTIONS)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    orig = (TREE / FILE).read_bytes()
    new = patch(orig)
    strips = [[Tim(dat, off).image().crop((0, Y0, 320, 240)) for dat in (orig, new)] for off, _, _ in CAPTIONS]
    sheet = Image.new("RGB", (644, 62 * len(strips)), (255, 0, 255))
    for k, (jp, en) in enumerate(strips):
        sheet.paste(jp, (0, 62 * k))
        sheet.paste(en, (324, 62 * k))
    sheet.resize((sheet.width * a.zoom, sheet.height * a.zoom), Image.NEAREST).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
