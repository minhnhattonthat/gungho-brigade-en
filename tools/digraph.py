"""Digraph font: English for the game's 11x11 SJIS fonts with no code change.

Both fonts look a glyph up by binary search in a sorted SJIS code list (glyph index = list position) and draw a 1bpp
11x11 bitmap (22 bytes, u16 big-endian rows, MSB = column 0) at a 12-px pitch. We keep the lists and redraw the
bitmaps of kana/kanji codes as letter pairs: two 5-px letters (fonts/font5.txt) at columns 0-4 and 6-10. A single
0x20 byte advances half a cell (verified in the marker build, docs/re/text.md §Font), so a pair never has to hold a
word-separating space unless the word has odd length.

Fonts (file holding the code list -> bitmap copies):
  GUNHO.EXE 0x5db78, 1376 codes -> GAMEDATA.DAT 0x346800 (stages, battle, intermission)
  MENU.EXE 0x2c59c, 1175 codes  -> TABLE/MENU.DAT 0x30800, TABLE/OVTABLE.DAT 0x0 (title menu, memory card)
Pair codes come from the kana/kanji codes (>= 0x829F) present in both lists first, so one code means the same pair in
every font; codes only in the GUNHO list are used after those, and only for text that GUNHO's font draws.

    python -X utf8 tools/digraph.py   # self-test
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT5 = ROOT / "fonts/font5.txt"
LISTS = {"gunho": ("GUNHO.EXE", 0x5DB78, 1376), "menu": ("MENU.EXE", 0x2C59C, 1175)}
BITMAPS = {"gunho": [("GAMEDATA.DAT", 0x346800)], "menu": [("TABLE/MENU.DAT", 0x30800), ("TABLE/OVTABLE.DAT", 0x0)]}
FIRST_PAIR_CODE = 0x829F  # ぁ: codes below are punctuation, digits, fullwidth Latin; kept (runtime text uses them)
TOP = 2  # cell row of font5 row 0
RAW = re.compile(r"(\{n\}|/|%[sd]|\[[0-9A-F]{2}\])")  # kept as bytes: line breaks, printf args, raw-byte tokens


def load_font5(path=FONT5):
    glyphs, cur = {}, None
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.startswith("="):
            cur = glyphs.setdefault(line[1:], [])
            assert len(line) == 2, line
        elif cur is not None and line:  # lines before the first glyph are comments
            assert len(line) == 5 and set(line) <= {".", "#"}, line
            cur.append(sum(1 << (4 - i) for i, ch in enumerate(line) if ch == "#"))
    glyphs[" "] = []
    for c, rows in glyphs.items():
        assert len(rows) <= 9, c
    return glyphs


GLYPHS = load_font5()


def code_list(tree, font):
    name, off, n = LISTS[font]
    raw = (Path(tree) / name).read_bytes()[off:off + 2 * n]
    return [struct.unpack_from(">H", raw, 2 * i)[0] for i in range(n)]


def pairs(text):
    """Split one text segment (no RAW tokens) into ('ab' pair | ' ' half-space) units."""
    out, i = [], 0
    while i < len(text):
        if text[i] == " ":
            out.append(" ")
            i += 1
        else:
            nxt = text[i + 1] if i + 1 < len(text) else " "
            out.append(text[i] + nxt)
            i += 2
    return out


def units(text):
    """-> list of bytes (raw tokens) and str units (pairs / ' ')."""
    out = []
    for k, part in enumerate(RAW.split(text)):
        if k % 2:
            out.append(b"\n" if part == "{n}" else b"/" if part == "/" else
                       bytes([int(part[1:3], 16)]) if part[0] == "[" else part.encode("ascii"))
        else:
            out.extend(pairs(part))
    return out


class Digraph:
    """Pair -> SJIS code map for one build, from every text the build draws with the 11x11 fonts."""

    def __init__(self, tree, gunho_texts, menu_texts):
        self.lists = {f: code_list(tree, f) for f in LISTS}
        both = set(self.lists["gunho"]) & set(self.lists["menu"])
        shared = sorted(c for c in both if c >= FIRST_PAIR_CODE)
        extra = sorted(c for c in self.lists["gunho"] if c >= FIRST_PAIR_CODE and c not in both)
        need = lambda texts: sorted({u for t in texts for u in units(t) if isinstance(u, str) and u != " "})  # noqa
        menu, gunho = need(menu_texts), need(gunho_texts)
        for p in set(menu) | set(gunho):
            bad = [c for c in p if c not in GLYPHS]
            if bad:
                raise ValueError(f"no glyph for {bad!r} (in {p!r})")
        rest = [p for p in gunho if p not in set(menu)]
        if len(menu) + len(rest) > len(shared) + len(extra) or len(menu) > len(shared):
            raise ValueError(f"digraph font full: {len(menu)} menu + {len(rest)} other pairs, "
                             f"{len(shared)} shared + {len(extra)} GUNHO-only codes")
        codes = shared + extra
        self.map = dict(zip(menu + rest, codes))

    def encode(self, text):
        out = bytearray()
        for u in units(text):
            out += u if isinstance(u, bytes) else b" " if u == " " else struct.pack(">H", self.map[u])
        return bytes(out)

    def patch_font(self, font, data, off):
        """Return `data` with the pair glyphs of this map drawn into the bitmap at `off`."""
        out = bytearray(data)
        index = {c: i for i, c in enumerate(self.lists[font])}
        for p, code in self.map.items():
            if code in index:
                out[off + 22 * index[code]:off + 22 * index[code] + 22] = glyph(p)
        return bytes(out)


def glyph(pair):
    rows = [0] * 11
    for k, ch in enumerate(pair):
        for r, bits in enumerate(GLYPHS[ch]):
            rows[TOP + r] |= bits << (11 - 6 * k)  # col 0 = bit 15; letter k at columns 6k..6k+4
    return struct.pack(">11H", *rows)


if __name__ == "__main__":
    assert pairs("Hi, Bob  x") == ["Hi", ", ", "Bo", "b ", " ", "x "], pairs("Hi, Bob  x")
    assert units("ab/c{n}%d[0A]") == ["ab", b"/", "c ", b"\n", b"%d", b"\n"]
    g = glyph("AB")
    assert struct.unpack_from(">H", g, 2 * TOP)[0] == 0b0111001111000000, bin(struct.unpack_from(">H", g, 4)[0])
    assert all(len(r) <= 9 for r in GLYPHS.values()) and len(GLYPHS) == 88, len(GLYPHS)
    print("selftest ok")
