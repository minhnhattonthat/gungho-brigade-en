"""ruler.py: marker build with ruler text filling the whole slot of chosen rows (width gate, phase 5).

    python -X utf8 tools/ruler.py PREFIX.. [--qa ID=TEXT ...]      e.g. gunho_ pilot_ ending_002 table_0043

Rows whose id starts with a PREFIX get "123456789A123456789B..." (each 10th char a letter: A = 10, B = 20, ...)
in every text part, shrunk until it fits the slot (`max` bytes); RAW tokens (%d, {n}) stay. All other rows get the
normal marker. Then run build.py and read the clip point off a shot: the last fully drawn char is the budget.
"""
import argparse
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
import insert  # noqa: E402
from digraph import RAW  # noqa: E402

RULER = "".join("123456789" + c for c in string.ascii_uppercase)


def ruler(row):
    kd = insert.kind(row)
    parts = RAW.split(row["jp"])
    texts = {k: RULER for k in range(0, len(parts), 2) if parts[k].strip()}
    while True:
        text = "".join(texts.get(k, p) if k % 2 == 0 else p for k, p in enumerate(parts))
        if insert.size(text, kd) <= int(row["max"] or 64):  # packed rows (ending_*): no slot; 64 chars > the 320-px screen
            return text
        k = max(texts, key=lambda k: len(texts[k]))
        texts[k] = texts[k][:-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prefix", nargs="+")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT")
    a = ap.parse_args()
    qa = {r["id"]: ruler(r) for rs in x.all_rows(x.TREE).values() for r in rs if r["id"].startswith(tuple(a.prefix))}
    qa.update(dict(s.split("=", 1) for s in a.qa))
    written, dg = insert.run(True, qa)
    print(f"{len(qa)} ruler rows, {len(dg.map)} digraph pairs; wrote {', '.join(written)}")


if __name__ == "__main__":
    assert ruler({"id": "t", "jp": "%d ﾉ ﾀﾞﾒｰｼﾞ", "max": "15", "_file": "X"}) == "%d123456789A123"
    main()
