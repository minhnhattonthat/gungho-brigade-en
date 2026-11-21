import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

unpacked = pytest.mark.skipif(not (build.DISC / "layout.xml").exists(), reason="disc not unpacked (run build.py)")


@unpacked
def test_overlay_file_replaces_tree_file(tmp_path):
    (tmp_path / "MOVIE").mkdir()
    (tmp_path / "MOVIE/S01A.STR").write_bytes(b"x")
    used = build.layout(tmp_path, tmp_path / "l.xml")
    assert used == ["MOVIE/S01A.STR"]
    src = {e.get("name"): e.get("source") for e in ET.parse(tmp_path / "l.xml").iter("file")}
    assert src["S01A.STR"] == str((tmp_path / "MOVIE/S01A.STR").resolve()) and src["GUNHO.EXE"] is None


@unpacked
def test_overlay_file_not_on_disc_is_refused(tmp_path):
    (tmp_path / "NOPE.BIN").write_bytes(b"x")
    with pytest.raises(SystemExit):
        build.layout(tmp_path, tmp_path / "l.xml")


@pytest.mark.slow
def test_unedited_rebuild_is_byte_identical(tmp_path):
    out, used = build.build(tmp_path / "id.bin", tmp_path / "empty")
    want = next(line.split()[0] for line in (ROOT / "rom.sha1").read_text().splitlines() if line.endswith(".bin"))
    with open(out, "rb") as f:
        assert hashlib.file_digest(f, "sha1").hexdigest() == want
    out.unlink()
