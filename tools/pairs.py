"""Review files, one per story stage: work/qa/story/chapters/sNN.txt (story order = stage order).

    python -X utf8 tools/pairs.py      then: qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"

Each row: `>> id | JP` then `   EN` (breaks shown as /). Regenerate after every script edit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/story/chapters"
PAGES = ROOT / "work/qa/story/pages"  # same rows in <3.6 KB pages, for reading


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    for old in PAGES.glob("*.txt"):
        old.unlink()
    n = 0
    for path in sorted((ROOT / "script").glob("scen_s*.tsv")):
        rows = [r for r in x.read_tsv(path) if r["jp"].strip()]
        text = "".join(f">> {r['id']} | {r['jp'].replace('{n}', '/')}\n   {r['en'].replace('{n}', '/')}\n" for r in rows)
        (OUT / f"{path.stem[5:]}.txt").write_text(text, encoding="utf-8", newline="\n")
        n += 1
        # pages under ~3.6 KB: the context plugin stubs any tool output over ~4 KB
        page, k = "", 0
        pairs = [a + b for a, b in zip(*[iter(text.splitlines(keepends=True))] * 2)]
        for p in pairs + [None]:
            if p is None or len((page + p).encode()) > 3600:
                if page:
                    (PAGES / f"{path.stem[5:]}_{k:02d}.txt").write_text(page, encoding="utf-8", newline="\n")
                    k += 1
                page = ""
            if p:
                page += p
    print(f"{n} chapter files in {OUT}")


if __name__ == "__main__":
    main()
