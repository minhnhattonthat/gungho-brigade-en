"""Voice subtitles (tools/voice.py, tools/asm/voicesubs.asm): the cue blob decodes back to the subtitles, and the
assembled hooks run under unicorn with exact-PC checks (draw path, XA_Play entry, stage load)."""
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import voice  # noqa: E402

unicorn = pytest.importorskip("unicorn")
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN, UC_HOOK_CODE  # noqa: E402
from unicorn.mips_const import (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3,  # noqa: E402
                                UC_MIPS_REG_PC, UC_MIPS_REG_RA, UC_MIPS_REG_SP, UC_MIPS_REG_S1,
                                UC_MIPS_REG_V0)

DATA = 0x8001E000


def cues(blob, clip):
    """[(start, end, [(x, y, width, text)])] of a clip in a blob."""
    o = struct.unpack_from("<H", blob, 0xC + 2 * clip)[0]
    out = []
    while o:
        s, e, t = struct.unpack_from("<HHH", blob, o)
        if s == 0xFFFF:
            break
        lines = []
        while blob[t] != 0xFF:
            x2, y, w2 = blob[t:t + 3]
            end = blob.index(0, t + 3)
            lines.append((x2 * 2, y, w2 * 2, blob[t + 3:end]))
            t = end + 1
        out.append((s, e, lines))
        o += 6
    return out


def test_blob_roundtrip():
    b = voice.blob(test=True)
    assert b[:4] == voice.MAGIC and struct.unpack_from("<i", b, 4)[0] == -1
    by = {}
    for fc, s, e, en in voice.rows(test=True):
        by.setdefault(fc, []).append((s, e, en))
    seen = 0
    for c, name, ch, ln in voice.clips():
        want = sorted(by.get(f"{name}_{ch:02d}", [])) if name != "XA000" else []
        got = cues(b, c)
        assert len(got) == len(want), c
        for (s, e, en), (v0, v1, lines) in zip(want, got):
            assert v0 == round(s * 60) and v1 > v0
            assert [t for *_, t in lines] == [voice.encode(t) for t in voice.wrap(en)]
            for x, y, w, t in lines:
                assert x + w <= 320 and y + 11 <= 240
            seen += 1
    assert seen


def test_wrap_and_encode():
    assert voice.wrap("short") == ["short"]
    a, b = voice.wrap("word " * 15)
    assert len(a) <= 50 and len(b) <= 50
    assert voice.encode("Hi, all!") == b"Hi" + bytes([voice_punct(",")]) + b" all" + bytes([voice_punct("!")])
    with pytest.raises(ValueError):
        voice.encode("a/b")
    with pytest.raises(ValueError):
        voice.wrap("x" * 120)


def voice_punct(ch):
    import smallfont
    return smallfont.PUNCT[ch]


@pytest.fixture(scope="module")
def exe(tmp_path_factory):
    out = tmp_path_factory.mktemp("voice")
    voice.apply(out, test=True)
    return (out / "GUNHO.EXE").read_bytes(), (out / "SCENFILE.DAT").read_bytes()


class PSX:
    """2 MB RAM; code runs at kseg0 0x80000000.. (unicorn's MIPS maps it to physical 0), host access is physical."""
    def __init__(self):
        self.uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_LITTLE_ENDIAN)
        self.uc.mem_map(0, 0x200000)

    def __getattr__(self, name):
        return getattr(self.uc, name)

    def mem_write(self, addr, data):
        self.uc.mem_write(addr & 0x1FFFFFFF, data)

    def mem_read(self, addr, size):
        return self.uc.mem_read(addr & 0x1FFFFFFF, size)


def machine(exe_bytes):
    mu = PSX()
    mu.mem_write(0x80020000, exe_bytes[0x800:])
    return mu


STUBS = {0x80036994: "READ", 0x80056B34: "DRAWPRIM", 0x80023034: "DRAWTEXT", 0x8005AD70: "DRAWOFS"}
DONE = 0x80001000   # return address of the call under test


def run(mu, pc, regs, limit=20000, stop=DONE):
    """Run from pc until it reaches stop (default: returns to DONE); stubbed functions log (name, a0..a3) and return.
    Any fetch outside the hook code, the stubs and the stop address faults (unmapped I/O) or misses the stop."""
    calls = []

    def hook(uc, addr, size, _):
        if addr in STUBS:
            calls.append((STUBS[addr], *(uc.reg_read(r) for r in (UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2,
                                                                     UC_MIPS_REG_A3))))
            if STUBS[addr] == "DRAWPRIM":
                a0 = uc.reg_read(UC_MIPS_REG_A0)
                calls[-1] = calls[-1] + (bytes(uc.mem_read(a0 & 0x1FFFFFFF, 20)),)
            uc.reg_write(UC_MIPS_REG_PC, uc.reg_read(UC_MIPS_REG_RA))
        elif addr == stop:
            uc.emu_stop()
    for a in STUBS:
        mu.mem_write(a, b"\0" * 8)
    mu.mem_write(DONE, b"\0" * 8)
    mu.hook_add(UC_HOOK_CODE, hook)
    mu.reg_write(UC_MIPS_REG_SP, 0x801FF000)
    mu.reg_write(UC_MIPS_REG_RA, DONE)
    for r, v in regs.items():
        mu.reg_write(r, v)
    mu.emu_start(pc, 0, count=limit)
    assert mu.reg_read(UC_MIPS_REG_PC) == stop, hex(mu.reg_read(UC_MIPS_REG_PC))
    assert mu.reg_read(UC_MIPS_REG_SP) == 0x801FF000
    return calls


SWAP_RESUME = 0x8005AEE8   # swap's third instruction; v0 must hold the buffer index (its displaced lui/lh)


def swap(mu):
    mu.mem_write(0x80155684, struct.pack("<h", 1))
    calls = run(mu, 0x8005AEE0, {}, stop=SWAP_RESUME)
    assert mu.reg_read(UC_MIPS_REG_V0) == 1
    assert mu.reg_read(UC_MIPS_REG_RA) == DONE   # GsSwapDispBuff's own return address survives
    return calls


def test_swap_hook_draws_due_cue(exe):
    gunho, scen = exe
    mu = machine(gunho)
    b = voice.blob(test=True)
    clip = next(c for c, *_ in voice.clips() if cues(b, c))
    (s, e, lines), *_ = cues(b, clip)
    mu.mem_write(DATA, b)
    mu.mem_write(DATA + 4, struct.pack("<iI", clip, 1000))
    mu.mem_write(0x800A1818, struct.pack("<i", -1))         # XA playing
    mu.mem_write(0x800A0678, struct.pack("<I", 1000 + s))   # first vsync of the cue
    calls = swap(mu)
    assert calls[0][0] == "DRAWOFS" and calls[0][1:3] == (0, 0)
    texts = [c for c in calls if c[0] == "DRAWTEXT"]
    assert [(c[2], c[3]) for c in texts] == [(x, y) for x, y, _, _ in lines]
    for c, (x, y, w, t) in zip(texts, lines):
        assert bytes(mu.mem_read(c[4], len(t) + 1)) == t + b"\0"
    band = [c for c in calls if c[0] == "DRAWPRIM"][0][5]
    tag, mode, color, xy, wh = struct.unpack("<5I", band)
    assert tag >> 24 == 4 and mode == 0xE1000400 and color == 0x62000000
    assert xy == (lines[0][1] << 16 | (lines[0][0] - 3)) and wh == (11 << 16 | (lines[0][2] + 6))


def test_swap_hook_quiet_when_not_due(exe):
    gunho, _ = exe
    mu = machine(gunho)
    b = voice.blob(test=True)
    clip = next(c for c, *_ in voice.clips() if cues(b, c))
    mu.mem_write(DATA, b)
    mu.mem_write(DATA + 4, struct.pack("<iI", clip, 1000))
    mu.mem_write(0x800A1818, struct.pack("<i", 0))           # XA stopped: the clip is dropped
    mu.mem_write(0x800A0678, struct.pack("<I", 1005))
    assert swap(mu) == []
    assert struct.unpack_from("<i", mu.mem_read(DATA + 4, 4))[0] == -1
    mu.mem_write(DATA, b"\0" * 4)                            # blob not loaded: nothing read, nothing drawn
    mu.mem_write(DATA + 4, struct.pack("<iI", clip, 1000))
    mu.mem_write(0x800A1818, struct.pack("<i", -1))
    assert swap(mu) == []


XASTART, XAPOS = 0x800A1C0C, 0x800A1C14


def test_swap_hook_starts_clock(exe):
    """The clock starts when the drive position passes the clip's first sector (start LBA + channel), back-dated by
    the sectors already played (3/8 vsync each); before that nothing is drawn and the clock stays 0."""
    gunho, _ = exe
    mu = machine(gunho)
    clip, _, ch, _ = next(t for t in voice.clips() if t[2] > 0)
    mu.mem_write(DATA, voice.blob(test=True))
    mu.mem_write(DATA + 4, struct.pack("<iI", clip, 0))
    mu.mem_write(0x800A1818, struct.pack("<i", -1))
    mu.mem_write(0x800A0678, struct.pack("<I", 4321))
    mu.mem_write(XASTART, struct.pack("<I", 70000))
    for pos in (70000, 70000 + ch):          # seeking / not at the clip's channel yet
        mu.mem_write(XAPOS, struct.pack("<I", pos))
        assert swap(mu) == []
        assert struct.unpack_from("<I", mu.mem_read(DATA + 8, 4))[0] == 0
    mu.mem_write(XAPOS, struct.pack("<I", 70000 + ch + 16))
    swap(mu)
    assert struct.unpack_from("<I", mu.mem_read(DATA + 8, 4))[0] == 4321 - 6


def test_xa_hook(exe):
    gunho, _ = exe
    mu = machine(gunho)
    mu.mem_write(DATA + 4, struct.pack("<iI", -1, 77))
    stop = 0x80051E34
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, _: uc.emu_stop() if a == stop else None)
    mu.reg_write(UC_MIPS_REG_SP, 0x801FF000)
    mu.reg_write(UC_MIPS_REG_A0, 117)
    mu.reg_write(UC_MIPS_REG_S1, 0x1234)
    mu.emu_start(0x80051E2C, 0, count=50)
    assert mu.reg_read(UC_MIPS_REG_PC) == stop
    assert mu.reg_read(UC_MIPS_REG_SP) == 0x801FF000 - 0x58
    assert struct.unpack("<iI", mu.mem_read(DATA + 4, 8)) == (117, 0)
    assert struct.unpack("<I", mu.mem_read(0x801FF000 - 0x58 + 0x4C, 4))[0] == 0x1234


@pytest.mark.parametrize("stage", [0, 8, 35, -1])
def test_stage_hook_reads_stage_blob(exe, stage):
    gunho, scen = exe
    mu = machine(gunho)
    mu.mem_write(0x80010000, struct.pack("<h", stage))
    word = struct.unpack_from("<I", gunho, 0x800316BC - 0x8001F800)[0]
    target = 0x80000000 | (word & 0x3FFFFFF) << 2
    calls = run(mu, target, {UC_MIPS_REG_A0: 0x80159170, UC_MIPS_REG_A1: 0x800EC490, UC_MIPS_REG_A2: 0x100,
                             UC_MIPS_REG_A3: 0x900})
    assert calls[0] == ("READ", 0x80159170, 0x800EC490, 0x100, 0x900)
    _, a0, a1, a2, a3 = calls[1]
    assert (a0, a1, a3 - a2) == (DATA, 0x800EC490, voice.ROOM) and a2 % 0x800 == 0 and a3 <= len(scen)
    assert scen[a2:a2 + 4] == voice.MAGIC
    per, common = voice.stage_clips()
    want = voice.blob(True, None, per[max(stage, 0)] | common)
    assert scen[a2:a2 + len(want)] == want
