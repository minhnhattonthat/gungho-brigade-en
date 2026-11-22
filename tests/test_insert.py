"""Phase 5: digraph font + inserter (marker build) against the original disc files."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import digraph as d  # noqa: E402
import extract as x  # noqa: E402
import insert as ins  # noqa: E402
import voice  # noqa: E402
from sjis import SJIS  # noqa: E402

pytestmark = pytest.mark.skipif(not (x.TREE / "GUNHO.EXE").exists(), reason="no unpacked disc (run build.py)")


def test_digraph_encode_and_glyphs():
    dg = d.Digraph(x.TREE, ["Hello, world/%d left"], ["Card error{n}"])
    enc = dg.encode("Hello, world/%d left")
    # He ll o, _ wo rl d_ | / | %d | _ le ft   (_ = one 0x20 half-space byte)
    assert len(enc) == 2 * 6 + 1 + 1 + 2 + 1 + 4 and enc.count(b"/") == 1 and b"%d" in enc
    menu = {u for u in d.units("Card error{n}") if isinstance(u, str) and u != " "}
    lists = {f: set(dg.lists[f]) for f in d.LISTS}
    assert all(dg.map[p] in lists["gunho"] and dg.map[p] in lists["menu"] for p in menu)
    assert min(dg.map.values()) >= d.FIRST_PAIR_CODE and len(set(dg.map.values())) == len(dg.map)
    gun = (x.TREE / "GAMEDATA.DAT").read_bytes()
    out = dg.patch_font("gunho", gun, 0x346800)
    changed = {(i - 0x346800) // 22 for i in range(len(gun)) if gun[i] != out[i]}
    assert changed <= {dg.lists["gunho"].index(c) for c in dg.map.values()}
    i = dg.lists["gunho"].index(dg.map["He"])
    assert out[0x346800 + 22 * i:0x346800 + 22 * i + 22] == d.glyph("He")


def test_digraph_rejects_missing_glyph():
    with pytest.raises(ValueError, match="no glyph"):
        d.Digraph(x.TREE, ["a~b"], [])


def test_markers_fit_and_keep_tokens():
    for rows in x.all_rows().values():
        for r in rows:
            m = ins.marker(r)
            assert ins.size(m, ins.kind(r)) <= len(SJIS.encode(r["jp"])), r["id"]
            assert d.RAW.findall(m) == d.RAW.findall(r["jp"]), r["id"]


def test_marker_build_writes_every_text_file(tmp_path):
    written, dg = ins.run(mode_marker=True, overlay=tmp_path)
    assert {"SCENFILE.DAT", "GUNHO.EXE", "TABLE.BIN", "MENU.EXE", "ENDING.BIN", "GAMEDATA.DAT"} <= set(written)
    for name in written:   # SCENFILE.DAT: up to the voice cue blobs appended after its last entry (tools/voice.py)
        size = voice.scen_end(tmp_path) if name == "SCENFILE.DAT" else (tmp_path / name).stat().st_size
        assert size == (x.TREE / name).stat().st_size, name
    scen = (tmp_path / "SCENFILE.DAT").read_bytes()
    row = x.scen_rows()["scen_s08"][0]
    assert scen[row["_off"]:row["_off"] + 2] == struct.pack(">H", dg.map["Th"])


def test_english_build_spaces(tmp_path):
    """Small-font spaces are 0xA0 (Unit-tab header stops at 0x20); help lines have no lone 0x20 (12-px cell);
    the config row 2 is a fullwidth space (D14)."""
    ins.run(overlay=tmp_path)
    rows = {r["id"]: r for rs in x.all_rows(x.TREE).values() for r in rs}
    exe = (tmp_path / "GUNHO.EXE").read_bytes()
    r = rows["gunho_01f18"]  # Dragoon 2 (in place)
    assert exe[r["_off"]:r["_off"] + 10] == b"Dragoon\xa02\0"
    r = rows["gunho_021e8"]  # help line
    assert b" " not in exe[r["_off"]:exe.index(b"\0", r["_off"])]
    tbl = (tmp_path / "TABLE.BIN").read_bytes()
    r = rows["table_00440"]
    assert tbl[r["_off"]:r["_off"] + 3] == "　".encode("cp932") + b"\0"
