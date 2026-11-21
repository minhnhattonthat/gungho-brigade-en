"""Replace rows of a translator output file: tl_patch.py bNNN FIXES.tsv (id<TAB>English per line).

Keeps every other row and the order; refuses ids not in the batch output.
"""
import sys
from pathlib import Path

batch, fixfile = sys.argv[1], sys.argv[2]
out = Path(f"work/tl/{batch}.out.tsv")
rows = [l.split("\t", 1) for l in out.read_text(encoding="utf8").splitlines()]
fix = dict(l.split("\t", 1) for l in Path(fixfile).read_text(encoding="utf8").splitlines() if l.strip())
ids = {r[0] for r in rows}
bad = set(fix) - ids
assert not bad, f"ids not in {out}: {sorted(bad)}"
out.write_text("".join(f"{i}\t{fix.get(i, e)}\n" for i, e in rows), encoding="utf8", newline="\n")
print(f"{out}: {len(fix)} rows replaced")
