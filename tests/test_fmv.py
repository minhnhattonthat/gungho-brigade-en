"""fmv.check (diffcheck for subtitled STRs): a changed video sector passes only inside a subtitled frame."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fmv  # noqa: E402


def sector(frame=None):
    s = bytearray(2336)
    if frame is None:
        s[2] = 0x64  # audio submode
    else:
        s[2] = 0x48  # video/data
        s[8:12] = b"\x60\x01\x01\x80"
        struct.pack_into("<HHI", s, 12, 0, 1, frame)
    return s


def test_check(monkeypatch):
    monkeypatch.setattr(fmv, "lines", lambda: [("S01A", 2, 2, "Hi")])
    old = sector(1) + sector() + sector(2)
    assert fmv.check(bytes(old), bytes(old), "S01A") == []
    for at in (2336 * 2 + 100, 2336 * 0 + 100, 2336 * 1 + 100):  # frame 2 ok; frame 1 and audio not
        new = bytearray(old)
        new[at] ^= 1
        assert bool(fmv.check(bytes(old), bytes(new), "S01A")) == (at < 2336 * 2), at
    assert fmv.check(bytes(old), bytes(old + sector()), "S01A")
