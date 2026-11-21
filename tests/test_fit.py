"""Every shipped string fits where insert.py writes it (tools/fitcheck.py, phase 7 gate)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import extract as x  # noqa: E402
import fitcheck  # noqa: E402


@pytest.mark.skipif(not (x.TREE / "SCENFILE.DAT").exists(), reason="no unpacked disc (work/disc/tree)")
def test_everything_fits():
    over, (eb, room) = fitcheck.overflows()
    assert not over, dict(over)
    assert eb <= room
