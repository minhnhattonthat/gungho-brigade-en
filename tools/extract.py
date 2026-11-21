"""Extract every Japanese string on the disc to script/*.tsv, and write strings back in place (roundtrip / insert base).

    python -X utf8 tools/extract.py            # writes missing script/*.tsv only
    python -X utf8 tools/extract.py --force    # overwrite (loses English!)

TSV columns: id, max, jp, en, notes. `max` = bytes the string may use in place (its slot, NUL excluded).
Sources (docs/re/text.md):
- SCENFILE.DAT stage overlays: strings = targets of the overlay's trailing u32 pointer table (load base 0x80159170).
  id `sNN_OOOO`: stage NN (= overlay stage id - 4), OOOO = offset in the overlay (RAM 0x80159170 + OOOO).
- EXE-like files: strings = lui/addiu or u32 references into the file's text ranges that decode as Japanese.
  id `<file>_<offset>`.
- GUNHO.EXE pilot records: 16-byte name field at the head of each 0x30-byte record.
- ENDING.BIN staff roll: one \\n-separated blob, one row per non-empty line (empty lines stay as in the original).
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mipsrefs import refs  # noqa: E402
from sjis import SJIS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "work/disc/tree"
SCRIPT = ROOT / "script"
COLS = ["id", "max", "jp", "en", "notes"]

OVL_BASE = 0x80159170
OVL_MAX = 0x5D60  # overlay buffer: TABLE.BIN loads at 0x8015eed0 (stage 29's overlay is exactly this size)
# SCENFILE entry -> offset of the stage overlay inside it (u32 stage id there; entries before it hold map data).
# Entry 106 carries a copy of entry 104's pointer table and no strings of its own: not an overlay.
OVERLAYS = {0: 0x0, 8: 0x780, 15: 0x780, 22: 0x700, 29: 0x700, 36: 0x780, 43: 0x780, 49: 0x780, 56: 0x780,
            63: 0x780, 69: 0x780, 70: 0x7BC, 77: 0x700, 84: 0x700, 85: 0x1BC, 92: 0x780, 99: 0x780, 104: 0x8,
            105: 0x324, 152: 0x780, 153: 0x130, 154: 0x50C, 155: 0xC8, 156: 0x3BC, 157: 0x694, 158: 0x32C,
            161: 0x780, 162: 0x40C, 163: 0x178, 164: 0x4CC, 165: 0x2A0, 169: 0x460, 170: 0x5AC, 171: 0x248,
            174: 0x780, 175: 0x134}
# Overlay strings that are pointer-table targets but not text (offset in overlay -> reason)
SCEN_DATA = {(0, 0x4): "fullwidth A-z charset list (font test), not shown as a line"}

# file -> (output name, RAM base of file byte 0 or None = PS-X EXE header, text ranges, data offsets -> reason)
EXES = {
    "GUNHO.EXE": ("gunho", None, [(0x800, 0x2400), (0x81000, 0x82300)], {}),
    "TABLE.BIN": ("table", 0x8015EED0, [(0x0, 0x500), (0x11500, 0x11C40)],
                  {0x11BAC: "ASCII -> fullwidth conversion list", 0x11BD8: "ASCII -> fullwidth conversion list"}),
    "MENU.EXE": ("menu", None, [(0x800, 0xA00), (0x2C500, 0x2D200)],
                 {0x2C59C: "glyph order list of the menu font", 0x2D0F0: "ASCII -> fullwidth conversion list",
                  0x2D11C: "ASCII -> fullwidth conversion list"}),
    "SLPS_019.02": ("slps", None, [(0x800, 0xA40)], {}),
    "MENUMV.EXE": ("menumv", None, [(0x800, 0xA40)], {}),
}
PILOTS = (0x776FC, 0x30, 16)  # GUNHO.EXE: first record, stride, name field size
# GUNHO.EXE name pool (unit/weapon/ability/part names + internal ASCII model names, 8-byte slots): reached only through
# u32 words in the unit/weapon/ability record tables (pool_refs asserts it), so it can be repacked (docs/re/text.md).
POOL = (0x82024, 0x82238)
ENDING = 0x2970  # ENDING.BIN staff roll blob start (NUL-terminated)
ENDING_LOAD, ENDING_REF = 0x8015eed0, 0x1584  # ENDING.BIN load address; file offset of the blob's only `addiu`
ENDING_ROOM = 0x12000  # bytes from ENDING_LOAD the relocated roll may reach (docs/re/text.md §Free space)

JP = re.compile(r"[　-ヿ一-鿿！-ﾟ]")
CLEAN = re.compile(r"[\x20-\x7e\n　-ヿ一-鿿！-￯‐-♯¥‾]+")


def cstr(data, off):
    return data[off:data.index(b"\0", off)]


def is_text(raw):
    try:
        t = raw.decode("cp932")
    except UnicodeDecodeError:
        return False
    return len(raw) >= 2 and CLEAN.fullmatch(t) is not None and JP.search(t) is not None


def dec(raw):
    return SJIS.decode(raw, 0, len(raw))[0]


def slots(starts, end):
    """Slot sizes: from each start to the next start (or `end`), sorted."""
    s = sorted(set(starts))
    return {a: b - a for a, b in zip(s, s[1:] + [end])}


def exe_base(data):
    return struct.unpack_from("<I", data, 0x18)[0] - 0x800 if data[:8] == b"PS-X EXE" else None


# --- SCENFILE ----------------------------------------------------------------------------------------------------
def scen_entries(tree=TREE):
    dat = (tree / "SCENFILE.DAT").read_bytes()
    ln = (tree / "SCENFILE.LEN").read_bytes()
    offs = list(struct.unpack(f"<{len(ln) // 4}I", ln))
    return dat, offs, offs[1:] + [len(dat)]


def pointer_table(ovl):
    """(start, end) of the trailing run of u32 pointers into the overlay buffer."""
    p = len(ovl) - 4
    inr = lambda q: OVL_BASE <= struct.unpack_from("<I", ovl, q)[0] < 0x80160000  # noqa: E731
    while not inr(p):
        p -= 4
    end = p + 4
    while inr(p):
        p -= 4
    return p + 4, end


def scen_overlay(dat, a, b, x):
    """-> (overlay bytes, stage, {offset: [table slot indices]}, text region end)"""
    ovl = dat[a + x:b]
    stage = struct.unpack_from("<I", ovl, 0)[0] - 4
    t0, t1 = pointer_table(ovl)
    tgt = {}
    for k, q in enumerate(range(t0, t1, 4)):
        tgt.setdefault(struct.unpack_from("<I", ovl, q)[0] - OVL_BASE, []).append(k)
    last = max(tgt)
    text_end = (last + len(cstr(ovl, last)) + 4) & ~3
    return ovl, stage, tgt, text_end


def scen_rows(tree=TREE):
    """-> {tsv name: rows}; row = dict(COLS) plus private keys _file/_off/_kind for write-back."""
    dat, offs, ends = scen_entries(tree)
    out = {}
    for e, x in OVERLAYS.items():
        ovl, stage, tgt, text_end = scen_overlay(dat, offs[e], ends[e], x)
        sz = slots(tgt, text_end)
        t0 = pointer_table(ovl)[0]
        base = offs[e] + x
        rows = []
        for o in sorted(tgt):
            if (stage, o) in SCEN_DATA:
                continue
            rows.append({"id": f"s{stage:02d}_{o:04x}", "max": str(sz[o] - 1), "jp": dec(cstr(ovl, o)), "en": "",
                         "notes": "", "_file": "SCENFILE.DAT", "_off": base + o, "_slot": sz[o],
                         # repack info: overlay file offset, text region end, file offsets of its pointer words
                         "_ovl": base, "_end": base + text_end, "_ptrs": [base + t0 + 4 * k for k in tgt[o]],
                         "_tail": ends[e]})
        out[f"scen_s{stage:02d}"] = rows
    return out


# --- EXE-like files ----------------------------------------------------------------------------------------------
def exe_strings(name, data):
    """Sorted text offsets in `name` (referenced, inside its text ranges, decoding as Japanese, not data)."""
    _, base, ranges, data_offs = EXES[name]
    base = exe_base(data) if base is None else base
    code = (0x800, len(data)) if data[:8] == b"PS-X EXE" else (0, len(data))
    found = set()
    for _, _, addr in refs(data, base, base, base + len(data), code):
        o = addr - base
        if any(lo <= o < hi for lo, hi in ranges) and o not in data_offs:
            if is_text(cstr(data, o)):
                found.add(o)
    return sorted(found)


def exe_rows(name, data):
    short = EXES[name][0]
    offs = exe_strings(name, data)
    rows = []
    for o in offs:
        raw = cstr(data, o)
        # NUL + padding to the next 4-aligned address; later zero words may be live variables, so not counted
        slot = (o + len(raw) + 4) & ~3
        rows.append({"id": f"{short}_{o:05x}", "max": str(slot - o - 1), "jp": dec(raw), "en": "", "notes": "",
                     "_file": name, "_off": o, "_slot": slot - o})
    return rows


def pilot_rows(data):
    first, stride, field = PILOTS
    rows, o = [], first
    while is_text(cstr(data, o)) and data[o + field - 1] == 0:
        rows.append({"id": f"pilot_{(o - first) // stride:03d}", "max": str(field - 1), "jp": dec(cstr(data, o)),
                     "en": "", "notes": "fixed 16-byte field", "_file": "GUNHO.EXE", "_off": o, "_slot": field})
        o += stride
    return rows


def ending_rows(data):
    blob = cstr(data, ENDING)
    rows, pos = [], ENDING
    for k, line in enumerate(blob.split(b"\n")):
        if line:
            rows.append({"id": f"ending_{k:03d}", "max": "", "jp": dec(line), "en": "", "notes": "staff roll line",
                         "_file": "ENDING.BIN", "_off": pos, "_slot": None})
        pos += len(line) + 1
    return rows


def all_rows(tree=TREE):
    out = scen_rows(tree)
    for name in EXES:
        out[EXES[name][0]] = exe_rows(name, (tree / name).read_bytes())
    out["pilots"] = pilot_rows((tree / "GUNHO.EXE").read_bytes())
    out["ending"] = ending_rows((tree / "ENDING.BIN").read_bytes())
    return out


# --- write back ---------------------------------------------------------------------------------------------------
def scen_layout(enc, pos, end, ovl_len):
    """Repacked overlay text: -> (how many strings stay in [pos, end), bytes appended after the overlay, rounded
    up to whole 0x800 sectors; 0 if all fit)."""
    n = 0
    while n < len(enc) and pos + len(enc[n]) + 1 <= end:
        pos += len(enc[n]) + 1
        n += 1
    rest = sum(len(b) + 1 for b in enc[n:])
    return n, -(-rest // 0x800) * 0x800


def roll_lines(lines):
    """Staff roll lines with rows that hold several lines ({n} -> 0x0A) split out. The pictures and the closing
    logos run on time, so the roll keeps its line count: each added line takes a blank from the next run of 2+
    blank lines after it (one blank always stays), and every section starts where it did."""
    out, pending, k = [], 0, 0
    while k < len(lines):
        if lines[k]:
            parts = lines[k].split(b"\n")
            pending += len(parts) - 1
            out += parts
            k += 1
            continue
        j = k
        while j < len(lines) and not lines[j]:
            j += 1
        drop = min(pending, j - k - 1)
        pending -= drop
        out += [b""] * (j - k - drop)
        k = j
    assert not pending and len(out) == len(lines), "staff roll: not enough blank lines to absorb {n} rows"
    return out


def write_back(name, data, rows, field="jp", encode=None, extra=None, tree=TREE):
    """Return a copy of file `name` with each row's `field` text written into its slot (NUL-padded).
    Rows whose `field` is empty keep the original bytes. Raises if a string does not fit its slot.
    `encode(row) -> bytes` overrides the default SJIS encoding of row[field]. `extra` (dict) receives other files
    the write changes (SCENFILE.LEN when an overlay grows)."""
    out = bytearray(data)
    enc_row = encode or (lambda r: SJIS.encode(r[field]))
    rows = [r for r in rows if r["_file"] == name]
    if name == "ENDING.BIN":
        blob = cstr(data, ENDING)
        lines = blob.split(b"\n")
        for r in rows:
            k = int(r["id"].split("_")[1])
            if r[field]:
                lines[k] = enc_row(r)
        new = b"\n".join(roll_lines(lines))
        room = ((ENDING + len(blob) + 4) & ~3) - ENDING - 1  # NUL + 4-alignment padding
        if len(new) <= room:
            out[ENDING:ENDING + room + 1] = new + bytes(room + 1 - len(new))
            return bytes(out)
        # Too long: append the blob at the 4-aligned file end (still inside the TABLE.BIN-sized load buffer; no
        # ENDING.BIN code refers past its end) and repoint its only reference, `addiu` at ENDING_REF (same lui half).
        at = (len(out) + 3) & ~3
        old, new_addr = ENDING_LOAD + ENDING, ENDING_LOAD + at
        assert (old + 0x8000) >> 16 == (new_addr + 0x8000) >> 16 and new_addr - ENDING_LOAD < ENDING_ROOM
        word = struct.unpack_from("<I", out, ENDING_REF)[0]
        assert word >> 26 == 0x09 and word & 0xFFFF == old & 0xFFFF, hex(word)
        struct.pack_into("<I", out, ENDING_REF, (word & 0xFFFF0000) | (new_addr & 0xFFFF))
        out[ENDING:ENDING + room + 1] = bytes(room + 1)  # the old Japanese roll, now unreferenced (jp_left)
        out[len(out):] = bytes(at - len(out)) + new + bytes(4 - len(new) % 4)
        return bytes(out)
    if name == "SCENFILE.DAT":
        # An overlay whose strings don't all fit in place is repacked: strings back to back (no 4-alignment) from
        # its first string to the text end, every pointer-table word rewritten. The table is the strings' only
        # reference (checked statically for all 36 overlays: no lui/addiu or other word points into the text).
        # Strings that still don't fit go after the overlay's end (= its LEN entry's end, after the pointer table):
        # the entry grows by whole 0x800 sectors (verified in game: any other growth hangs the next stage load)
        # and SCENFILE.LEN is rewritten into extra["SCENFILE.LEN"]. Overlays are done last-first so offsets hold.
        inserts = []
        for ovl in sorted({r["_ovl"] for r in rows}, reverse=True):
            group = sorted((r for r in rows if r["_ovl"] == ovl), key=lambda r: r["_off"])
            enc = [enc_row(r) if r[field] else cstr(data, r["_off"]) for r in group]
            if all(len(b) < r["_slot"] for b, r in zip(enc, group)):
                for b, r in zip(enc, group):
                    if r[field]:
                        out[r["_off"]:r["_off"] + r["_slot"]] = b + bytes(r["_slot"] - len(b))
                continue
            pos, end, tail = group[0]["_off"], group[0]["_end"], group[0]["_tail"]
            n_in, grow = scen_layout(enc, pos, end, tail - ovl)
            if tail - ovl + grow > OVL_MAX:
                raise ValueError(f"{group[0]['id'][:3]}: overlay {tail - ovl:#x} + {grow:#x} > {OVL_MAX:#x}")
            out[pos:end] = bytes(end - pos)
            extra_bytes = bytearray()
            for k, (b, r) in enumerate(zip(enc, group)):
                if k < n_in:
                    at, here = pos, out
                    pos += len(b) + 1
                else:
                    at, here = tail + len(extra_bytes), None
                    extra_bytes += b + b"\0"
                if here is not None:
                    out[at:at + len(b)] = b
                for p in r["_ptrs"]:
                    struct.pack_into("<I", out, p, OVL_BASE + at - ovl)
            if grow:
                out[tail:tail] = bytes(extra_bytes) + bytes(grow - len(extra_bytes))
                inserts.append((tail, grow))
        if extra is not None and inserts:
            ln = (tree / "SCENFILE.LEN").read_bytes()
            offs = struct.unpack(f"<{len(ln) // 4}I", ln)
            extra["SCENFILE.LEN"] = struct.pack(f"<{len(offs)}I", *(o + sum(g for p, g in inserts if p <= o)
                                                                       for o in offs))
        elif inserts:
            raise ValueError("SCENFILE.DAT grew: pass extra={} to get the new SCENFILE.LEN")
        return bytes(out)
    if name == "GUNHO.EXE":
        pool = [r for r in rows if POOL[0] <= r["_off"] < POOL[1]]
        if any(r[field] and len(enc_row(r)) >= r["_slot"] for r in pool):
            out = repack_pool(out, data, pool, enc_row, field)
            rows = [r for r in rows if r not in pool]
    for r in rows:
        if not r[field]:
            continue
        enc = enc_row(r)
        if len(enc) >= r["_slot"]:
            raise ValueError(f"{r['id']}: {len(enc)} bytes > max {r['_slot'] - 1}")
        o = r["_off"]
        out[o:o + r["_slot"]] = enc + bytes(r["_slot"] - len(enc))
    return bytes(out)


def pool_refs(data):
    """-> (RAM base, {pool string offset: [file offsets of the u32 words pointing at it]}). Raises if anything but
    a data word points into the pool, or a word points inside a string."""
    base = exe_base(data)
    by = {}
    for site, kind, addr in refs(data, base, base + POOL[0], base + POOL[1], (0x800, len(data))):
        assert kind == "word", f"{kind} at {site:#x} points into the name pool ({addr:#x}): repack would break it"
        by.setdefault(addr - base, []).append(site)
    starts = sorted(by)
    for a, b in zip(starts, starts[1:]):
        assert a + len(cstr(data, a)) < b, f"pool ref into the middle of the string at {a:#x}"
    return base, by


def repack_pool(out, data, pool_rows, enc_row, field):
    """The name pool rewritten back to back (byte-aligned; every reader uses lbu) and each pointer word updated.
    Unreferenced bytes are dropped; strings without a row (ASCII model names) keep their bytes."""
    base, by = pool_refs(data)
    at = {r["_off"]: r for r in pool_rows}
    pos = POOL[0]
    out[POOL[0]:POOL[1]] = bytes(POOL[1] - POOL[0])
    for o in sorted(by):
        r = at.get(o)
        b = enc_row(r) if r and r[field] else cstr(data, o)
        if pos + len(b) + 1 > POOL[1]:
            raise ValueError(f"name pool full: {r['id'] if r else hex(o)} needs {pos + len(b) + 1 - POOL[1]} more bytes")
        out[pos:pos + len(b)] = b
        for site in by[o]:
            struct.pack_into("<I", out, site, base + pos)
        pos += len(b) + 1
    return out


# --- TSV ----------------------------------------------------------------------------------------------------------
def write_tsv(path, rows):
    lines = ["\t".join(COLS)]
    for r in rows:
        vals = [r[c] for c in COLS]
        assert not any("\t" in v or "\n" in v for v in vals), r["id"]
        lines.append("\t".join(vals))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def read_tsv(path):
    lines = path.read_text(encoding="utf-8-sig").split("\n")
    assert lines[0].split("\t") == COLS, f"{path}: header {lines[0]!r}"
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line:
            continue
        vals = line.split("\t")
        if len(vals) != len(COLS):
            raise ValueError(f"{path}:{n}: {len(vals)} columns, want {len(COLS)}")
        rows.append(dict(zip(COLS, vals)))
    return rows


def main(argv):
    force = "--force" in argv
    SCRIPT.mkdir(exist_ok=True)
    n = 0
    for name, rows in all_rows().items():
        path = SCRIPT / f"{name}.tsv"
        if path.exists() and not force:
            continue
        write_tsv(path, rows)
        n += 1
    print(f"wrote {n} files to {SCRIPT}")


if __name__ == "__main__":
    main(sys.argv[1:])
