"""fitcheck.py: list every translated string that does not fit its in-place slot (what insert.py would refuse).

    python -X utf8 tools/fitcheck.py [-v]

Per file: rows over their slot (bytes over), and the ENDING.BIN staff roll total. -v prints every row.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
import insert as ins  # noqa: E402
from digraph import Digraph  # noqa: E402


def overflows(tree=x.TREE):
    """-> ({file: [(id, bytes, max)]}, (ending bytes, ending room)) for the current script `en`."""
    rows = [r for rs in x.all_rows(tree).values() for r in rs]
    en = {r["id"]: r["en"] for p in x.SCRIPT.glob("*.tsv") for r in x.read_tsv(p)}
    for r in rows:
        r["new"] = en.get(r["id"], "")
    big = [r for r in rows if r["new"] and ins.kind(r) == "pair"]
    roll = ins.aligned
    dg = Digraph(tree, [r["new"] for r in big if not roll(r)], [], [r["new"] for r in big if roll(r)])

    def encode(r):
        kd = ins.kind(r)
        return (dg.encode(r["new"], roll(r)) if kd == "pair" else
                ins.SJIS.encode(ins.to_full(r["new"]) if kd == "full" else r["new"]))

    over = defaultdict(list)
    ending = [0, 0]
    data = (tree / "SCENFILE.DAT").read_bytes()
    for ovl in sorted({r["_ovl"] for r in rows if "_ovl" in r}):
        # repacked overlay (extract.write_back): text region, then whole sectors after the overlay up to OVL_MAX
        group = sorted((r for r in rows if r.get("_ovl") == ovl), key=lambda r: r["_off"])
        enc = [encode(r) if r["new"] else x.cstr(data, r["_off"]) for r in group]
        ovl_len = group[0]["_tail"] - ovl
        _, grow = x.scen_layout(enc, group[0]["_off"], group[0]["_end"], ovl_len)
        if ovl_len + grow > x.OVL_MAX:
            over["SCENFILE.DAT"].append((group[0]["id"][:3], ovl_len + grow, x.OVL_MAX))
    exe = [r for r in rows if r["_file"] == "GUNHO.EXE"]
    try:  # the name pool is repacked as a whole (extract.repack_pool): only its total size can overflow
        x.write_back("GUNHO.EXE", (tree / "GUNHO.EXE").read_bytes(), exe, field="new", encode=encode, tree=tree)
    except ValueError as e:
        if str(e).startswith("name pool"):
            over["GUNHO.EXE"].append(("name pool", str(e), x.POOL[1] - x.POOL[0]))
    for r in rows:
        if not r["new"] or "_ovl" in r or r["_file"] == "GUNHO.EXE" and x.POOL[0] <= r["_off"] < x.POOL[1]:
            continue
        n = len(encode(r))
        if r["_slot"] is None:
            ending[0] += n + 1
        elif n >= r["_slot"]:
            over[r["_file"]].append((r["id"], n, r["_slot"] - 1))
    data = (tree / "ENDING.BIN").read_bytes()
    blob = x.cstr(data, x.ENDING)
    lines = blob.split(b"\n")
    done = {int(r["id"].split("_")[1]) for r in rows if r["_file"] == "ENDING.BIN" and r["new"]}
    ending[0] += sum(len(ln) + 1 for k, ln in enumerate(lines) if k not in done) - 1
    ending[1] = x.ENDING_ROOM - ((len(data) + 3) & ~3) - 1  # relocated to the file end when it outgrows its slot
    return over, tuple(ending)


def main():
    over, (eb, room) = overflows()
    for name, rs in sorted(over.items()):
        print(f"{name}: {len(rs)} rows over, {sum(n - m for _, n, m in rs)} bytes")
        if "-v" in sys.argv:
            for i, n, m in rs:
                print(f"  {i}: {n} > {m}")
    print(f"ENDING.BIN staff roll: {eb} / {room} bytes")
    return 1 if over or eb > room else 0


if __name__ == "__main__":
    sys.exit(main())
