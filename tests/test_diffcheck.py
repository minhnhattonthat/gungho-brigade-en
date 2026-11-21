"""The shipped insert writes only inside its allowed ranges (tools/diffcheck.py), and diffcheck catches writes that
aren't: a flipped byte in an EXE and in a SCENFILE overlay, junk appended to ENDING.BIN. Also the static claims the
repacks rely on: nothing but the pointer table reaches overlay text, nothing but u32 words reaches the name pool."""
import shutil
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import diffcheck  # noqa: E402
import extract as x  # noqa: E402
import insert  # noqa: E402
import smallfont  # noqa: E402
from mipsrefs import refs  # noqa: E402

pytestmark = pytest.mark.skipif(not (x.TREE / "SCENFILE.DAT").exists(), reason="no unpacked disc (work/disc/tree)")


@pytest.fixture(scope="module")
def overlay(tmp_path_factory):
    out = tmp_path_factory.mktemp("overlay") / "files"
    insert.run(overlay=out)
    return out


def flipped(overlay, tmp_path, name, off):
    bad = tmp_path / "files"
    shutil.copytree(overlay, bad)
    data = bytearray((bad / name).read_bytes())
    data[off] ^= 0xFF
    (bad / name).write_bytes(data)
    return bad


def test_insert_is_clean(overlay):
    assert diffcheck.main(overlay, verbose=False) == 0


def test_flipped_exe_byte_fails(overlay, tmp_path):
    assert diffcheck.main(flipped(overlay, tmp_path, "GUNHO.EXE", 0x1000), verbose=False) == 1


def test_flipped_overlay_code_byte_fails(overlay, tmp_path):
    lo = struct.unpack("<2I", (x.TREE / "SCENFILE.LEN").read_bytes()[:8])
    assert diffcheck.main(flipped(overlay, tmp_path, "SCENFILE.DAT", lo[1] + 0x10), verbose=False) == 1


def test_junk_after_ending_fails(overlay, tmp_path):
    bad = tmp_path / "files"
    shutil.copytree(overlay, bad)
    with open(bad / "ENDING.BIN", "ab") as f:
        f.write(bytes(0x10000))
    assert diffcheck.main(bad, verbose=False) == 1


def test_smallfont_only_touches_its_ranges():
    for name in smallfont.files():
        old = (x.TREE / name).read_bytes()
        new = smallfont.patch(name, old)
        diff = [i for i in range(len(old)) if old[i] != new[i]]
        assert diff and all(any(lo <= i < hi for lo, hi in smallfont.ranges(name)) for i in diff), name


def test_name_pool_only_reached_by_words():
    _, by = x.pool_refs((x.TREE / "GUNHO.EXE").read_bytes())  # asserts inside
    assert min(by) == x.POOL[0] and len(by) > 60


def test_overlay_text_only_reached_by_pointer_table():
    rows = [r for rs in x.scen_rows().values() for r in rs]
    data = (x.TREE / "SCENFILE.DAT").read_bytes()
    for ovl in sorted({r["_ovl"] for r in rows}):
        group = [r for r in rows if r["_ovl"] == ovl]
        first, end, tail = min(r["_off"] for r in group), group[0]["_end"], group[0]["_tail"]
        blob = data[ovl:tail]
        table = {p - ovl for r in group for p in r["_ptrs"]}
        hits = [(site, kind) for site, kind, _ in refs(blob, x.OVL_BASE, x.OVL_BASE + first - ovl,
                                                       x.OVL_BASE + end - ovl) if site not in table]
        assert not hits, f"{group[0]['id'][:3]}: {hits[:5]}"
