"""Phase 4: extraction roundtrip and coverage, run against the original disc files (work/disc/tree)."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract as x  # noqa: E402
from sjis import SJIS  # noqa: E402

pytestmark = pytest.mark.skipif(not (x.TREE / "GUNHO.EXE").exists(), reason="no unpacked disc (run build.py)")

# Japanese-looking NUL-bounded runs that are not text (offset -> reason). Keyed by file.
NOT_TEXT = {
    "GUNHO.EXE": {0x2AA8: "code", 0x5DB78: "big-font glyph order list"},
    "MENU.EXE": {0x1C910: "binary data", 0x2C59C: "menu font glyph list", 0x2D0F0: "ASCII->fullwidth list", 0x2D11C: "ASCII->fullwidth list"},
    "TABLE.BIN": {0x11BAC: "ASCII->fullwidth list", 0x11BD8: "ASCII->fullwidth list"},
}
MEDIA = re.compile(r"\.(STR|XA|VB|VH)$")  # FMV, voice, sound banks
CONTAINER = re.compile(r"\.(DAT|LEN|dat)$")  # image/model data: half-width matches there are noise


@pytest.fixture(scope="module")
def rows():
    return x.all_rows()


@pytest.fixture(scope="module")
def files():
    return {p.name: p.read_bytes() for p in x.TREE.iterdir() if p.is_file()}


def flat(rows):
    return [r for v in rows.values() for r in v]


def test_codec_roundtrip(rows, files):
    for r in flat(rows):
        raw = files[r["_file"]][r["_off"]:]
        raw = raw[:raw.index(b"\n" if r["_file"] == "ENDING.BIN" else b"\0")]
        assert SJIS.encode(r["jp"]) == raw, r["id"]
        assert not re.search(r"\[[0-9A-F]{2}\]", r["jp"]), f"{r['id']}: undecoded byte"


def test_write_back_is_identity(rows, files):
    """Writing every jp string back into its slot (NUL-padded) reproduces each file: slots hold nothing else."""
    for name in {r["_file"] for r in flat(rows)}:
        assert x.write_back(name, files[name], flat(rows)) == files[name], name


def test_scen_repack(rows, files):
    """A string longer than its slot repacks its overlay; every pointer still reaches its own string."""
    import struct
    group = [dict(r) for r in rows["scen_s10"]]  # s10: ~400 bytes of slack in its region
    group[0]["jp"] = "Ａ" * (group[0]["_slot"] // 2 + 3)
    out = x.write_back("SCENFILE.DAT", files["SCENFILE.DAT"], group)
    assert out != files["SCENFILE.DAT"]
    for r in group:
        for p in r["_ptrs"]:
            addr = struct.unpack_from("<I", out, p)[0]
            assert x.dec(x.cstr(out, r["_ovl"] + addr - x.OVL_BASE)) == r["jp"], r["id"]


def test_scen_grow(rows, files):
    """Text over the region goes after the overlay: entry grows by whole sectors, LEN shifts later entries only,
    every pointer reaches its string, the overlay before it is untouched."""
    import struct
    group = [dict(r) for r in rows["scen_s10"]]
    for r in group:
        r["jp"] = "Ａ" * 40
    extra = {}
    out = x.write_back("SCENFILE.DAT", files["SCENFILE.DAT"], group, extra=extra)
    grow = len(out) - len(files["SCENFILE.DAT"])
    assert grow > 0 and grow % 0x800 == 0
    tail = group[0]["_tail"]
    assert out[:group[0]["_ovl"]] == files["SCENFILE.DAT"][:group[0]["_ovl"]]
    assert out[tail + grow:] == files["SCENFILE.DAT"][tail:]
    old = struct.unpack(f"<{len(extra['SCENFILE.LEN']) // 4}I", (x.TREE / "SCENFILE.LEN").read_bytes())
    new = struct.unpack(f"<{len(old)}I", extra["SCENFILE.LEN"])
    assert [n - o for o, n in zip(old, new)] == [grow if o >= tail else 0 for o in old]
    for r in group:
        for p in r["_ptrs"]:
            addr = struct.unpack_from("<I", out, p)[0]
            assert addr - x.OVL_BASE < x.OVL_MAX
            assert x.dec(x.cstr(out, r["_ovl"] + addr - x.OVL_BASE)) == r["jp"], r["id"]


def test_ending_relocate(rows, files):
    """A staff roll longer than its slot moves to the file end; the one addiu points there."""
    import struct
    group = [dict(r) for r in rows["ending"]]
    for r in group:
        r["jp"] = "Ａ" * 20
    out = x.write_back("ENDING.BIN", files["ENDING.BIN"], group)
    at = (len(files["ENDING.BIN"]) + 3) & ~3
    lo = struct.unpack_from("<I", out, x.ENDING_REF)[0] & 0xFFFF
    assert lo == (x.ENDING_LOAD + at) & 0xFFFF
    assert x.cstr(out, at).split(b"\n")[int(group[0]["id"].split("_")[1])] == SJIS.encode("Ａ" * 20)


def test_overlays(files):
    dat, offs, ends = x.scen_entries()
    stages = []
    for e, off in x.OVERLAYS.items():
        ovl, stage, tgt, text_end = x.scen_overlay(dat, offs[e], ends[e], off)
        stages.append(stage)
        assert min(tgt) == 4, f"entry {e}: first string not right after the stage id"
        assert all(ovl[o - 1] == 0 for o in tgt if o > 4), f"entry {e}: pointer into the middle of a string"
        t0, _ = x.pointer_table(ovl)
        assert text_end <= t0
    assert sorted(stages) == list(range(36)), stages


def test_ids_unique_and_tsv_in_sync(rows):
    ids = [r["id"] for r in flat(rows)]
    assert len(ids) == len(set(ids))
    for name, v in rows.items():
        path = x.SCRIPT / f"{name}.tsv"
        assert path.exists(), f"{path} missing: run tools/extract.py"
        got = {r["id"]: r for r in x.read_tsv(path)}
        assert set(got) == {r["id"] for r in v}, name
        for r in v:
            assert got[r["id"]]["jp"] == r["jp"], f"{r['id']}: jp column edited"
            assert got[r["id"]]["max"] == r["max"], r["id"]


def jp_runs(data, half=True):
    """4-aligned NUL-bounded runs that decode as cp932 and look Japanese (kana + kanji, or mostly half-width kana).
    Every string the game stores is 4-aligned (docs/re/text.md); unaligned matches are code and image noise."""
    for m in re.finditer(rb"(?<=\x00)[^\x00]{3,}(?=\x00)", data):
        if m.start() % 4:
            continue
        try:
            t = m.group().decode("cp932")
        except UnicodeDecodeError:
            continue
        if re.search(r"[\x00-\x09\x0b-\x1f-]", t):
            continue
        kana = len(re.findall(r"[ぁ-ヿ]", t))
        kanji = len(re.findall(r"[一-鿿]", t))
        nhalf = len(re.findall(r"[ｦ-ﾟ]", t))
        if kana >= 2 and 2 * (kana + kanji) >= 0.5 * len(m.group()) or half and nhalf >= 3 and nhalf >= 0.6 * len(t):
            yield m.start(), m.end()


def test_coverage_exe_files(rows, files):
    """Every Japanese-looking run in every program file lies inside an extracted string or a known non-text list."""
    spans = {}
    for r in flat(rows):
        n = len(SJIS.encode(r["jp"]))
        spans.setdefault(r["_file"], []).append((r["_off"], r["_off"] + n))
    missed = []
    for path in x.TREE.rglob("*"):
        name = path.relative_to(x.TREE).as_posix()
        if not path.is_file() or MEDIA.search(name) or name == "SCENFILE.DAT":  # SCENFILE: next test
            continue
        data = path.read_bytes()
        for a, b in jp_runs(data, half=not CONTAINER.search(name)):
            if any(a < e and s < b for s, e in spans.get(name, [])) or a in NOT_TEXT.get(name, {}):
                continue
            missed.append(f"{name}+{a:#x} {data[a:b].decode('cp932')[:30]!r}")
    assert not missed, "\n".join(missed)


def test_coverage_scenfile(rows):
    """SCENFILE: no Japanese-looking run in any entry outside the overlays' extracted strings.

    Overlays hold no half-width kana, so only full-width runs count (half-width matches are map-data noise). Runs
    that are byte copies of extracted overlay text are stale buffer residue in non-overlay entries (e.g. entry 17
    starts with stage 2 lines and breaks off into binary mid-string); the game reads text via the overlay tables."""
    dat, offs, ends = x.scen_entries()
    scen = [r for r in flat(rows) if r["_file"] == "SCENFILE.DAT"]
    spans = [(r["_off"], r["_off"] + len(SJIS.encode(r["jp"]))) for r in scen]
    known = b"\0".join(SJIS.encode(r["jp"]) for r in scen)
    data_ok = {(offs[e] + off + o) for e, off in x.OVERLAYS.items() for (st, o) in x.SCEN_DATA
               if x.scen_overlay(dat, offs[e], ends[e], off)[1] == st}
    missed = [f"SCENFILE+{a:#x} {dat[a:b].decode('cp932')[:30]!r}" for a, b in jp_runs(dat, half=False)
              if a not in data_ok and not any(a < e and s < b for s, e in spans) and dat[a:b] not in known]
    assert not missed, f"{len(missed)} runs:\n" + "\n".join(missed[:40])
