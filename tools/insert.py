"""insert.py: write every translated (or marker) string and the digraph font into the build overlay.

    python -X utf8 tools/insert.py [--marker] [--qa ID=TEXT ...]

Rewrites work/build/files/ (build.py swaps those files in). Text per row: `--qa` override, else the marker (with
--marker), else the TSV `en` column; rows with none keep their Japanese bytes. Rows whose Japanese is half-width only
(unit, weapon, pilot names, battle messages: the small 8x12 font) are written as plain ASCII; MENU.EXE / SLPS /
MENUMV rows as fullwidth Latin (see FULLWIDTH_FILES); all other rows go through the digraph font (tools/digraph.py).
Where strings go (extract.write_back): EXE/TABLE/pilot rows in place (longer than the slot fails the build), except
the GUNHO.EXE name pool, which is repacked with its u32 pointers rewritten; a SCENFILE overlay whose strings don't fit
is repacked and may grow by whole sectors; the ENDING.BIN roll moves to the file end when it outgrows its blob.
Then the digraph font bitmaps and the small-font pitch/glyphs (tools/smallfont.py) go onto the written files.

Marker (phase 5): each line becomes filler of the same half-cell width as the Japanese line, with `[id]` at the start
of the widest line, so every box shows which row it is without growing; markers never take more bytes than the JP.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
import gfx_captions  # noqa: E402
import gfx_labels  # noqa: E402
import smallfont  # noqa: E402
from digraph import BITMAPS, RAW, Digraph, units  # noqa: E402
from sjis import SJIS  # noqa: E402

OVERLAY = x.ROOT / "work/build/files"
STRINGS = x.ROOT / "build/strings.tsv"
GFX = [gfx_labels, gfx_captions]  # graphics redraws: module with FILE, patch(data), ranges(name) (diffcheck)
# Title-side exes and TABLE.BIN's memory-card screens draw with a font keyed by the real SJIS code (the patched
# bitmaps never show there: verified, title GAME LOAD and intermission GAME SAVE showed the kana of the pair codes),
# so their text goes out as fullwidth Latin, 12 px per letter.
FULLWIDTH_FILES = {"MENU.EXE", "SLPS_019.02", "MENUMV.EXE", "TABLE.BIN"}
# Memory-card save titles: the BIOS card manager shows them (real SJIS), the game writes digits into fixed offsets.
# Fullwidth Latin already; no marker (a translation must keep the digit positions).
SAVE_TITLES = {"table_11800", "table_11844", "table_11ac4"}
FILLER = "The quick brown fox jumps over the lazy dog. 0123456789 "
SMALL = re.compile(r"[\x20-\x7e｡-ﾟ]*")


def kind(row):
    """'small' (half-width 8x12 font, ASCII), 'full' (fullwidth Latin) or 'pair' (digraph font)."""
    if SMALL.fullmatch(row["jp"]):
        return "small"
    return "full" if row["_file"] in FULLWIDTH_FILES or row["id"] in SAVE_TITLES else "pair"


def small_font(row):
    return kind(row) == "small"


def to_full(text):
    """ASCII -> fullwidth (space -> U+3000); RAW tokens (line breaks, %s, [XX]) kept."""
    return "".join(p if k % 2 else "".join("　" if c == " " else chr(ord(c) + 0xFEE0) if c.isascii() else c for c in p)
                   for k, p in enumerate(RAW.split(text)))


def half_cells(s):
    return sum(1 if SMALL.fullmatch(ch) else 2 for ch in s)


def size(text, kd):
    """Encoded byte count, before the pair map exists (a pair = 2 bytes, a half-space = 1)."""
    if kd != "pair":
        return len(SJIS.encode(to_full(text) if kd == "full" else text))
    return sum(len(u) if isinstance(u, bytes) else 1 if u == " " else 2 for u in units(text))


def marker(row):
    """Marker text for `row`: same line structure and width as the JP, encoded size <= the JP's."""
    kd = kind(row)
    parts = RAW.split(row["jp"])
    per = 2 if kd == "full" else 1  # half-cells per letter
    widths = [half_cells(p) // per if k % 2 == 0 else 0 for k, p in enumerate(parts)]
    label = re.sub(r"[^A-Za-z0-9]", "", row["id"]).upper() if kd == "small" else f"[{row['id']}]"
    widest = max(range(0, len(parts), 2), key=lambda k: widths[k])
    texts = {}
    for k in range(0, len(parts), 2):
        fill = FILLER if kd != "small" else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        texts[k] = ((label + " " if k == widest else "") + fill * 9)[:widths[k]]
    limit = len(SJIS.encode(row["jp"]))
    while True:
        text = "".join(texts[k] if k % 2 == 0 else p for k, p in enumerate(parts))
        if size(text, kd) <= limit:
            return text
        k = max(texts, key=lambda k: len(texts[k]))  # shrink the longest line
        texts[k] = texts[k][:-1]


def text_key(b):
    """djb2-xor of a string's bytes: the key tools/lua/textcover.lua logs, so coverage survives relocation."""
    h = 5381
    for c in b:
        h = (((h << 5) + h) & 0xFFFFFFFF) ^ c
    return h


def write_strings(rows, encode, path):
    """build/strings.tsv for textcover.py: id, key of the bytes the game reads (a staff-roll row = its own line)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            b = encode(r) if r["new"] else SJIS.encode(r["jp"])
            b = b.split(b"\n")[0] if r["_file"] == "ENDING.BIN" else b  # textcover keys a roll line up to its 0x0A
            f.write(f"{r['id']}\t{text_key(b):08X}\n")


def run(mode_marker=False, qa=None, overlay=OVERLAY, tree=x.TREE, strings=None):
    qa = qa or {}
    files = x.all_rows(tree)
    en = {}
    for path in x.SCRIPT.glob("*.tsv"):
        for r in x.read_tsv(path):
            en[r["id"]] = r["en"]
    rows = [r for rs in files.values() for r in rs]
    unknown = set(qa) - {r["id"] for r in rows}
    if unknown:
        sys.exit(f"--qa ids not in the script: {sorted(unknown)}")
    for r in rows:
        mark = mode_marker and r["id"] not in SAVE_TITLES
        r["new"] = qa.get(r["id"]) or (marker(r) if mark else en.get(r["id"], ""))
    big = [r for r in rows if r["new"] and kind(r) == "pair"]
    roll = lambda r: r["_file"] == "ENDING.BIN"  # noqa: E731  staff roll: glyphs on whole cells only
    dg = Digraph(tree, [r["new"] for r in big if not roll(r)], [], [r["new"] for r in big if roll(r)])

    def encode(r):
        kd = kind(r)
        return (dg.encode(r["new"], roll(r)) if kd == "pair" else
                SJIS.encode(to_full(r["new"]) if kd == "full" else r["new"]))

    if strings:
        write_strings(rows, encode, strings)
    if overlay.exists():
        shutil.rmtree(overlay)
    written = []
    for name in sorted({r["_file"] for r in rows if r["new"]}):
        data = (tree / name).read_bytes()
        extra = {}
        out = x.write_back(name, data, [r for r in rows if r["_file"] == name], field="new", encode=encode,
                           extra=extra, tree=tree)
        for fname, blob in [(name, out), *extra.items()]:
            dest = overlay / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(blob)
            written.append(fname)
    def current(name):  # the overlay copy when text was already written to it, so a font write never undoes it
        dest = overlay / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        return dest, (dest if dest.exists() else tree / name).read_bytes()

    for font, copies in BITMAPS.items():
        for name, off in copies:
            dest, data = current(name)
            dest.write_bytes(dg.patch_font(font, data, off))
            written.append(name)
    for name in smallfont.files():
        dest, data = current(name)
        dest.write_bytes(smallfont.patch(name, data))
        written.append(name)
    for g in GFX:
        dest, data = current(g.FILE)
        dest.write_bytes(g.patch(data))
        written.append(g.FILE)
    return sorted(set(written)), dg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT")
    a = ap.parse_args()
    qa = dict(s.split("=", 1) for s in a.qa)
    written, dg = run(a.marker, qa, strings=STRINGS)
    print(f"{len(dg.map)} digraph pairs; wrote {', '.join(written)}")


if __name__ == "__main__":
    main()
