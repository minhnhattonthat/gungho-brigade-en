"""Save editor (tools/debug/save.py): checksums match a game-written save, and an edit keeps them valid."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/debug"))
import save  # noqa: E402

FIXTURE = ROOT / "work/saves/i08_saved.mcd"   # game-written (regenerate: tools/debug/warp.py i08 + save route)


@pytest.mark.skipif(not FIXTURE.exists(), reason="game-written save fixture not present (work/ is gitignored)")
def test_checksums_match_game_and_edit(tmp_path):
    card = FIXTURE.read_bytes()
    base = save.find_save(card)
    blk = card[base:base + 0x2000]
    assert struct.unpack_from("<II", blk, 0x100) == save.checksums(blk)
    out = tmp_path / "e.mcd"
    assert save.main([str(FIXTURE), "--out", str(out), "--stage", "20", "--poke", "0x4:4=0x1234"]) == 0
    e = out.read_bytes()[base:base + 0x2000]
    assert struct.unpack_from("<h", e, 0x108)[0] == 20
    assert struct.unpack_from("<I", e, 0x10c)[0] == 0x1234
    assert struct.unpack_from("<II", e, 0x100) == save.checksums(e)


def test_checksum_formula_synthetic():
    blk = bytearray(range(256)) * 32
    a, b = save.checksums(blk)
    assert a == sum(blk[:0x100]) + sum(blk[0x108:0x110])
    assert b == sum(blk[0x108:0x2000])
