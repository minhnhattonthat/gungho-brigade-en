"""Battle command-menu labels: GAMEDATA.DAT entry 265 +0x131c, a 96x140 4bpp TIM of 14 buttons (docs/re/graphics.md).

    python -X utf8 tools/gfx_labels.py OUT.png [--zoom 4]     # preview the English sheet (tools/insert.py applies it)

Left column 7 buttons 40x20 (face x 3-36), right column 5 buttons + 2 blank 56x20 (face x 43-92), rows 20 px apart,
face rows 3-16. Each face is cleared with the blank right button's face (rows 100-119, same gradient per row), then
the label is drawn in the font5 letters (fonts/font5.txt, proportional: blank columns trimmed, 1-px gap, space 3),
ink index 0 like the Japanese, centred, caps from face row 6. Labels follow glossary.md (decision D13).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digraph import GLYPHS  # noqa: E402
from gfx import TREE, Tim  # noqa: E402
from PIL import Image  # noqa: E402

FILE, OFF = "GAMEDATA.DAT", 0x361B38
LEFT = ["Shoot", "Melee", "Item", "Morph", "Special", "Equip", "End"]
RIGHT = ["Unit List", "Save", "Goals", "Config", "End Plot"]
FACES = [(3, 36), (43, 92)]  # face x ranges, left and right column
BLANK_Y = 100  # the first blank right button
INK, CAP_TOP, FACE_Y = 0, 6, (3, 16)


def columns(word):
    """Column bitmasks (bit r = font5 row r) of `word`, proportional."""
    cols = []
    for ch in word:
        if ch == " ":
            cols += [0, 0, 0]
            continue
        rows = GLYPHS[ch]
        g = [sum(1 << r for r, bits in enumerate(rows) if bits >> (4 - i) & 1) for i in range(5)]
        while g and not g[0]:
            g.pop(0)
        while g and not g[-1]:
            g.pop()
        if ch in "il":  # stem only: "Special" needs it to fit the 34-px face
            g = [max(g, key=lambda m: bin(m).count("1"))]
        cols += g + [0]
    while cols and not cols[-1]:
        cols.pop()
    return cols


def patch(data):
    data = bytearray(data)
    t = Tim(data, OFF)
    for side, words in enumerate([LEFT, RIGHT]):
        lo, hi = FACES[side]
        for k, word in enumerate(words):
            y0 = 20 * k
            for y in range(FACE_Y[0], FACE_Y[1] + 1):
                for x in range(lo, hi + 1):
                    t.set(x, y0 + y, t.get(FACES[1][0] + x - lo, BLANK_Y + y))
            cols = columns(word)
            assert len(cols) <= hi - lo + 1, f"{word!r} is {len(cols)} px, face {hi - lo + 1}"
            x0 = lo + (hi - lo + 1 - len(cols)) // 2
            for i, m in enumerate(cols):
                for r in range(9):
                    if m >> r & 1:
                        t.set(x0 + i, y0 + CAP_TOP + r, INK)
    t.write(data)
    return bytes(data)


def ranges(name):
    """Byte ranges of `name` this patch may change (tools/diffcheck.py)."""
    if name != FILE:
        return []
    t = Tim((TREE / FILE).read_bytes(), OFF)
    return [(t.px_off, t.px_off + len(t.px))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    orig = (TREE / FILE).read_bytes()
    imgs = [Tim(d, OFF).image() for d in (orig, patch(orig))]
    w, h = imgs[0].size
    sheet = Image.new("RGB", (2 * w + 4, h), (255, 0, 255))
    sheet.paste(imgs[0], (0, 0))
    sheet.paste(imgs[1], (w + 4, 0))
    sheet.resize((sheet.width * a.zoom, h * a.zoom), Image.NEAREST).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
