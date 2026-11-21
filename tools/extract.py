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
ENDING = 0x2970  # ENDING.BIN staff roll blob start (NUL-terminated)

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
        rows = []
        for o in sorted(tgt):
            if (stage, o) in SCEN_DATA:
                continue
            rows.append({"id": f"s{stage:02d}_{o:04x}", "max": str(sz[o] - 1), "jp": dec(cstr(ovl, o)), "en": "",
                         "notes": "", "_file": "SCENFILE.DAT", "_off": offs[e] + x + o, "_slot": sz[o]})
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
def write_back(name, data, rows, field="jp", encode=None):
    """Return a copy of file `name` with each row's `field` text written into its slot (NUL-padded).
    Rows whose `field` is empty keep the original bytes. Raises if a string does not fit its slot.
    `encode(row) -> bytes` overrides the default SJIS encoding of row[field]."""
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
        new = b"\n".join(lines)
        room = ((ENDING + len(blob) + 4) & ~3) - ENDING - 1  # NUL + 4-alignment padding
        if len(new) > room:
            raise ValueError(f"ENDING.BIN staff roll: {len(new)} bytes > {room}")
        out[ENDING:ENDING + room + 1] = new + bytes(room + 1 - len(new))
        return bytes(out)
    for r in rows:
        if not r[field]:
            continue
        enc = enc_row(r)
        if len(enc) >= r["_slot"]:
            raise ValueError(f"{r['id']}: {len(enc)} bytes > max {r['_slot'] - 1}")
        o = r["_off"]
        out[o:o + r["_slot"]] = enc + bytes(r["_slot"] - len(enc))
    return bytes(out)


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
