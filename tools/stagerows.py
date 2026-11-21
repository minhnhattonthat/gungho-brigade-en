"""stagerows.py sNN [N]: the N rows of stage sNN whose encoded English grew most over the JP (bytes), to pick
rewording candidates when fitcheck.py reports a SCENFILE overlay over its room. Run from the repo root."""
import sys
sys.path.insert(0, "tools")
import extract as x
import insert as ins
from digraph import Digraph
st = sys.argv[1]
rows = x.read_tsv(x.SCRIPT / f"scen_{st}.tsv")
allen = [r["en"] for p in x.SCRIPT.glob("scen_*.tsv") for r in x.read_tsv(p) if r["en"]]
dg = Digraph(x.TREE, allen, [])
out = []
for r in rows:
    e = len(dg.encode(r["en"])) if r["en"] else 0
    j = len(ins.SJIS.encode(r["jp"]))
    out.append((e - j, e, j, r["id"], r["en"]))
print(st, "en", sum(o[1] for o in out), "jp", sum(o[2] for o in out))
for d, e, j, i, en in sorted(out, reverse=True)[: int(sys.argv[2]) if len(sys.argv) > 2 else 15]:
    print(f"{i}\t+{d}\t{e}\t{en}")
