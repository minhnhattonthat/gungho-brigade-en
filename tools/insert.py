"""insert.py: write every translated (or marker) string and the digraph font into the build overlay.

    python -X utf8 tools/insert.py [--marker] [--qa ID=TEXT ...]

Rewrites work/build/files/ (build.py swaps those files in). Text per row: `--qa` override, else the marker (with
--marker), else the TSV `en` column; rows with none keep their Japanese bytes. Rows whose Japanese is half-width only
(unit, weapon, pilot names, battle messages: the small 8x12 font) are written as plain ASCII; all other rows go
through the digraph font (tools/digraph.py). In-place only: a string longer than its slot fails the build.

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
from digraph import BITMAPS, RAW, Digraph, units  # noqa: E402
from sjis import SJIS  # noqa: E402

OVERLAY = x.ROOT / "work/build/files"
MENU_FONT_FILES = {"MENU.EXE", "SLPS_019.02", "MENUMV.EXE", "TABLE.BIN"}  # pairs from codes valid in both fonts
FILLER = "The quick brown fox jumps over the lazy dog. 0123456789 "
SMALL = re.compile(r"[\x20-\x7e｡-ﾟ]*")


def small_font(row):
    return SMALL.fullmatch(row["jp"]) is not None


def half_cells(s):
    return sum(1 if SMALL.fullmatch(ch) else 2 for ch in s)


def size(text, small):
    """Encoded byte count, before the pair map exists (a pair = 2 bytes, a half-space = 1)."""
    if small:
        return len(SJIS.encode(text))
    return sum(len(u) if isinstance(u, bytes) else 1 if u == " " else 2 for u in units(text))


def marker(row):
    """Marker text for `row`: same line structure and width as the JP, encoded size <= the JP's."""
    small = small_font(row)
    parts = RAW.split(row["jp"])
    widths = [half_cells(p) if k % 2 == 0 else 0 for k, p in enumerate(parts)]
    label = re.sub(r"[^A-Za-z0-9]", "", row["id"]).upper() if small else f"[{row['id']}]"
    widest = max(range(0, len(parts), 2), key=lambda k: widths[k])
    texts = {}
    for k in range(0, len(parts), 2):
        fill = FILLER if not small else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        texts[k] = ((label + " " if k == widest else "") + fill * 9)[:widths[k]]
    limit = len(SJIS.encode(row["jp"]))
    while True:
        text = "".join(texts[k] if k % 2 == 0 else p for k, p in enumerate(parts))
        if size(text, small) <= limit:
            return text
        k = max(texts, key=lambda k: len(texts[k]))  # shrink the longest line
        texts[k] = texts[k][:-1]


def run(mode_marker=False, qa=None, overlay=OVERLAY, tree=x.TREE):
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
        r["new"] = qa.get(r["id"]) or (marker(r) if mode_marker else en.get(r["id"], ""))
    big = [r for r in rows if r["new"] and not small_font(r)]
    dg = Digraph(tree, [r["new"] for r in big if r["_file"] not in MENU_FONT_FILES],
                 [r["new"] for r in big if r["_file"] in MENU_FONT_FILES])

    def encode(r):
        return SJIS.encode(r["new"]) if small_font(r) else dg.encode(r["new"])

    if overlay.exists():
        shutil.rmtree(overlay)
    written = []
    for name in sorted({r["_file"] for r in rows if r["new"]}):
        data = (tree / name).read_bytes()
        out = x.write_back(name, data, [r for r in rows if r["_file"] == name], field="new", encode=encode)
        dest = overlay / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(out)
        written.append(name)
    for font, copies in BITMAPS.items():
        for name, off in copies:
            dest = overlay / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(dg.patch_font(font, (tree / name).read_bytes(), off))
            written.append(name)
    return written, dg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT")
    a = ap.parse_args()
    qa = dict(s.split("=", 1) for s in a.qa)
    written, dg = run(a.marker, qa)
    print(f"{len(dg.map)} digraph pairs; wrote {', '.join(written)}")


if __name__ == "__main__":
    main()
