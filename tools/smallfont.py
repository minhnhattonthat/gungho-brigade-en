"""Small 8x12 font (unit, pilot, weapon, skill names) at a 6-px pitch: about 1.3x the letters per window.

Engine: the three loops that draw a half-width string advance x by 8 per byte (`addiu $s1,$s1,8`); patched to 6.
They draw the STATUS / TUNE UP / battle status names (TABLE.BIN), the battle hover box and the second GUNHO.EXE loop.
Glyphs: ASCII letters, digits and `:` redrawn from fonts/font5.txt (5 px white + 1 px dark shadow on the right, as
the original glyphs) in both copies of the font TIM, so they fit the pitch; `@` (the game's mm glyph) is redrawn as
two small m's stacked. Kana glyphs are untouched (no English row uses them). docs/re/text.md §Small font.

    python -X utf8 tools/smallfont.py   # self-test against the pristine disc files
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digraph import GLYPHS  # noqa: E402

PITCH = 6
ADDIU_S1_8 = 0x26310008
ADVANCES = [("TABLE.BIN", 0x33E0), ("GUNHO.EXE", 0x3924), ("GUNHO.EXE", 0x190BC)]  # file offsets of the advance
TIMS = [("GAMEDATA.DAT", 0x363A90), ("TABLE/MENU.DAT", 0x29000)]  # 4bpp 128x132, 16 glyphs x 12 rows (0x30-0xDF)
TIM_PIXELS = 0x40  # TIM header 8 + CLUT block 44 + image block header 12
W, CELL_W, CELL_H, TOP = 128, 8, 11, 2  # TOP: cell row of font5 row 0
WHITE, SHADOW = 2, 1  # CLUT indices of the original glyphs
CHARS = "0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# Word space in names: the STATUS Unit-tab header stops at a 0x20 (JP names had none), so insert.py writes 0xA0, a
# cell (unused in JIS X 0201) drawn blank here.
SPACE = 0xA0
# Punctuation for the voice subtitles (tools/voice.py): the TIM starts at 0x30, so ASCII punctuation has no cell.
# Drawn in the precomposed ガ..ボ row (0x80-0x8F), reached in JP only by merging a DE/DF dakuten byte into a kana;
# English text has neither. voice.py encodes these characters as PUNCT[ch].
PUNCT = {ch: 0x80 + i for i, ch in enumerate("!\"'(),-.?;&%…*+")}
MM = [0b10100, 0b11111, 0b10101, 0b10101, 0, 0b10100, 0b11111, 0b10101, 0b10101]  # `@` = mm, rows from cell row 1


def cell(rows, top):
    """8x11 cell of CLUT indices from 5-bit rows (bit 4 = column 0): white ink + a shadow pixel right of it."""
    px = [[0] * CELL_W for _ in range(CELL_H)]
    for r, bits in enumerate(rows):
        for k in range(5):
            if bits >> (4 - k) & 1:
                px[top + r][k] = WHITE
    for line in px:
        for k in range(CELL_W - 1):
            if line[k] == WHITE and line[k + 1] == 0:
                line[k + 1] = SHADOW
    return px


def put_cell(out, base, code, px):
    gx, gy = (code & 15) * CELL_W, ((code >> 4) - 3) * CELL_H
    for y in range(CELL_H):
        for x in range(CELL_W):
            o = base + ((gy + y) * W + gx + x) // 2
            sh = 4 * ((gx + x) & 1)
            out[o] = (out[o] & ~(15 << sh)) | (px[y][x] << sh)


def ranges(name):
    """Byte ranges of `name` this module may change (for diffcheck)."""
    rs = [(off, off + 4) for f, off in ADVANCES if f == name]
    rs += [(off + TIM_PIXELS, off + TIM_PIXELS + W * CELL_H * 12 // 2) for f, off in TIMS if f == name]
    return rs


def patch(name, data):
    """`data` (file `name`, pristine or already text-patched) with the pitch and glyph changes applied."""
    out = bytearray(data)
    for f, off in ADVANCES:
        if f == name:
            word = struct.unpack_from("<I", out, off)[0]
            assert word == ADDIU_S1_8, f"{name} {off:#x}: {word:#x} is not addiu $s1,$s1,8"
            struct.pack_into("<I", out, off, (ADDIU_S1_8 & ~0xFFFF) | PITCH)
    for f, off in TIMS:
        if f == name:
            assert out[off:off + 4] == b"\x10\0\0\0" and struct.unpack_from("<I", out, off + 0x34)[0] == 12 + W * 132 // 2 \
                and struct.unpack_from("<HH", out, off + 0x3C) == (W // 4, 132), f"{name} {off:#x}: not the font TIM"
            for ch in CHARS:
                put_cell(out, off + TIM_PIXELS, ord(ch), cell(GLYPHS[ch], TOP))
            put_cell(out, off + TIM_PIXELS, ord("@"), cell(MM, 1))
            put_cell(out, off + TIM_PIXELS, SPACE, cell([], 0))
            for ch, code in PUNCT.items():
                put_cell(out, off + TIM_PIXELS, code, cell(GLYPHS[ch], TOP))
    return bytes(out)


def files():
    return sorted({f for f, _ in ADVANCES} | {f for f, _ in TIMS})


if __name__ == "__main__":
    import extract as x
    for name in files():
        old = (x.TREE / name).read_bytes()
        new = patch(name, old)
        diff = [i for i in range(len(old)) if old[i] != new[i]]
        assert diff and all(any(lo <= i < hi for lo, hi in ranges(name)) for i in diff), name
        print(f"{name}: {len(diff)} bytes changed, all inside {ranges(name)}")
    print("smallfont self-test ok")
