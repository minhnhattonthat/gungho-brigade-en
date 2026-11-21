"""diffcheck.py: every byte the build overlay changes must lie in a range the text/font insert is allowed to write.

    python -X utf8 tools/diffcheck.py [-v]

Compares work/build/files/<file> with the pristine work/disc/tree/<file> (the per-file romdiff: mkpsxiso rebuilds the
disc, so a raw .bin diff would show every moved sector). Allowed: string slots (EXEs, TABLE.BIN, pilot fields), the
ENDING.BIN staff roll + its addiu + an appended blob, each SCENFILE overlay's text region + pointer table + whole
sectors appended after it (entries compared one by one through the old and new SCENFILE.LEN), the font bitmaps.
Exit 1 on any byte changed outside them, or a file of unexpected size.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
from digraph import BITMAPS, LISTS  # noqa: E402

OVERLAY = x.ROOT / "work/build/files"


def outside(old, new, ranges, grow_at=None):
    """Offsets where old != new outside [lo, hi) ranges; new may be longer only past grow_at (then allowed)."""
    n = min(len(old), len(new))
    ok = bytearray(n)
    for lo, hi in ranges:
        ok[max(lo, 0):min(hi, n)] = b"\1" * max(0, min(hi, n) - max(lo, 0))
    bad = [i for i in range(n) if old[i] != new[i] and not ok[i]]
    if len(new) != len(old) and (grow_at is None or len(new) < len(old)):
        bad.append(n)
    return bad


def file_ranges(name, rows, data):
    rs = [(r["_off"], r["_off"] + r["_slot"]) for r in rows if r["_file"] == name and r["_slot"]]
    if name == "ENDING.BIN":
        blob = x.cstr(data, x.ENDING)
        rs += [(x.ENDING, (x.ENDING + len(blob) + 4) & ~3), (x.ENDING_REF, x.ENDING_REF + 4)]
    for font, copies in BITMAPS.items():
        for fname, off in copies:
            if fname == name:
                rs.append((off, off + 22 * LISTS[font][2]))
    return rs


def check_scen(rows, tree, verbose):
    old, new = (tree / "SCENFILE.DAT").read_bytes(), (OVERLAY / "SCENFILE.DAT").read_bytes()
    lo = struct.unpack(f"<{len((tree / 'SCENFILE.LEN').read_bytes()) // 4}I", (tree / "SCENFILE.LEN").read_bytes())
    lpath = OVERLAY / "SCENFILE.LEN"
    ln = struct.unpack(f"<{len(lo)}I", lpath.read_bytes()) if lpath.exists() else lo
    oe, ne = list(lo[1:]) + [len(old)], list(ln[1:]) + [len(new)]
    ovl_of = {}
    for r in rows:
        if r["_file"] == "SCENFILE.DAT":
            ovl_of.setdefault(r["_tail"], r)
    bad = 0
    for e in range(len(lo)):
        a, b = old[lo[e]:oe[e]], new[ln[e]:ne[e]]
        r = ovl_of.get(oe[e])
        allowed = []
        if r:
            base = lo[e]
            ovl = x.scen_overlay(old, lo[e], oe[e], r["_ovl"] - lo[e])
            t0, t1 = x.pointer_table(ovl[0])
            first = min(q["_off"] for q in rows if q.get("_ovl") == r["_ovl"])
            allowed = [(first - base, r["_end"] - base), (r["_ovl"] - base + t0, r["_ovl"] - base + t1)]
        grow = len(b) - len(a)
        if grow and (not r or grow % 0x800):
            print(f"SCENFILE.DAT entry {e}: size {len(a):#x} -> {len(b):#x}")
            bad += 1
            continue
        hits = outside(a, b, allowed, grow_at=len(a) if grow else None)
        if hits:
            bad += 1
            print(f"SCENFILE.DAT entry {e}: {len(hits)} bytes outside, first at entry +{hits[0]:#x}")
    return bad


def main():
    verbose = "-v" in sys.argv
    tree = x.TREE
    rows = [r for rs in x.all_rows(tree).values() for r in rs]
    bad = 0
    for path in sorted(p for p in OVERLAY.rglob("*") if p.is_file()):
        name = path.relative_to(OVERLAY).as_posix()
        if name == "SCENFILE.LEN":
            continue
        if name == "SCENFILE.DAT":
            n = check_scen(rows, tree, verbose)
        else:
            old, new = (tree / name).read_bytes(), path.read_bytes()
            hits = outside(old, new, file_ranges(name, rows, old), grow_at=len(old) if name == "ENDING.BIN" else None)
            n = len(hits)
            if hits:
                print(f"{name}: {n} bytes outside allowed ranges, first at {hits[0]:#x}")
        bad += bool(n)
        if verbose or n:
            print(f"{name}: {'BAD' if n else 'ok'}")
    print("diffcheck:", "FAIL" if bad else "ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
