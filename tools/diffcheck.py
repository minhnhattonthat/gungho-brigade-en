"""diffcheck.py: every byte the build overlay changes must lie in a range the text/font insert is allowed to write.

    python -X utf8 tools/diffcheck.py [-v]

Compares work/build/files/<file> with the pristine work/disc/tree/<file> (the per-file romdiff: mkpsxiso rebuilds the
disc, so a raw .bin diff would show every moved sector). Allowed: string slots (EXEs, TABLE.BIN, pilot fields), the
ENDING.BIN staff roll + its addiu + an appended blob, each SCENFILE overlay's text region + pointer table + whole
sectors appended after it (entries compared one by one through the old and new SCENFILE.LEN), the font bitmaps,
and in a subtitled .STR only the video sectors of frames script/fmv/subs.tsv puts a line on (fmv.check); the voice
subtitle hooks in GUNHO.EXE and their cue blobs after SCENFILE.DAT's last entry (tools/voice.py).
Exit 1 on any byte changed outside them, or a file of unexpected size.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
import fmv  # noqa: E402
import smallfont  # noqa: E402
import voice  # noqa: E402
from digraph import BITMAPS, LISTS  # noqa: E402
from insert import GFX  # noqa: E402

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
    if name == "GUNHO.EXE":  # repacked name pool + its pointer words
        rs += [x.POOL] + [(s, s + 4) for sites in x.pool_refs(data)[1].values() for s in sites]
    for font, copies in BITMAPS.items():
        for fname, off in copies:
            if fname == name:
                rs.append((off, off + 22 * LISTS[font][2]))
    return rs + smallfont.ranges(name) + voice.ranges(name) + [r for g in GFX for r in g.ranges(name)]


def ending_tail(old, new):
    """Problems with ENDING.BIN growth: only the relocated roll may be appended (extract.write_back), at the 4-aligned
    old end, NUL-terminated with < 4 bytes of zero padding, and the addiu at ENDING_REF must point at it."""
    if len(new) <= len(old):
        return []
    at = (len(old) + 3) & ~3
    blob = x.cstr(new, at) if b"\0" in new[at:] else new[at:]
    pad = new[at + len(blob):]
    word = struct.unpack_from("<I", new, x.ENDING_REF)[0]
    bad = []
    if any(new[len(old):at]) or not blob or len(pad) > 4 or any(pad):
        bad.append("ENDING.BIN: appended bytes are not one NUL-terminated roll")
    if word & 0xFFFF != (x.ENDING_LOAD + at) & 0xFFFF:
        bad.append(f"ENDING.BIN: addiu at {x.ENDING_REF:#x} does not point at the appended roll")
    if at + len(blob) >= x.ENDING_ROOM:
        bad.append("ENDING.BIN: roll runs past the load buffer")
    return bad


def check_scen(rows, tree, overlay):
    old, new = (tree / "SCENFILE.DAT").read_bytes(), (overlay / "SCENFILE.DAT").read_bytes()
    bad = 0
    end = voice.scen_end(overlay, tree)
    if len(new) > end:   # voice cue blobs (tools/voice.py): sector-aligned after the last entry, starting 'VSUB'
        at = -(-end // 0x800) * 0x800
        if any(new[end:at]) or new[at:at + 4] != voice.MAGIC or (len(new) - at) % 0x800:
            print("SCENFILE.DAT: bytes after the last entry are not the voice cue blobs")
            bad += 1
        new = new[:end]
    lo = struct.unpack(f"<{len((tree / 'SCENFILE.LEN').read_bytes()) // 4}I", (tree / "SCENFILE.LEN").read_bytes())
    lpath = overlay / "SCENFILE.LEN"
    ln = struct.unpack(f"<{len(lo)}I", lpath.read_bytes()) if lpath.exists() else lo
    oe, ne = list(lo[1:]) + [len(old)], list(ln[1:]) + [len(new)]
    ovl_of = {}
    for r in rows:
        if r["_file"] == "SCENFILE.DAT":
            ovl_of.setdefault(r["_tail"], r)
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


def main(overlay=OVERLAY, verbose=None):
    verbose = "-v" in sys.argv if verbose is None else verbose
    tree = x.TREE
    rows = [r for rs in x.all_rows(tree).values() for r in rs]
    bad = 0
    for path in sorted(p for p in overlay.rglob("*") if p.is_file()):
        name = path.relative_to(overlay).as_posix()
        if name == "SCENFILE.LEN":
            continue
        if name == "SCENFILE.DAT":
            n = check_scen(rows, tree, overlay)
        elif name.endswith(".STR"):  # subtitled FMV: only video sectors of subtitled frames
            hits = fmv.check((tree / name).read_bytes(), path.read_bytes(), path.stem)
            for h in hits:
                print(h)
            n = len(hits)
        else:
            old, new = (tree / name).read_bytes(), path.read_bytes()
            hits = outside(old, new, file_ranges(name, rows, old), grow_at=len(old) if name == "ENDING.BIN" else None)
            tail = ending_tail(old, new) if name == "ENDING.BIN" else []
            n = len(hits) + len(tail)
            if hits:
                print(f"{name}: {len(hits)} bytes outside allowed ranges, first at {hits[0]:#x}")
            for t in tail:
                print(t)
        bad += bool(n)
        if verbose or n:
            print(f"{name}: {'BAD' if n else 'ok'}")
    print("diffcheck:", "FAIL" if bad else "ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
