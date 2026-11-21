"""Find references to addresses in a PS1 executable or overlay: lui/addiu (and lui/ori, lui + load/store) pairs, and
plain u32 data pointers. Used by extract.py to find string starts and by insertion to know what to repoint.

    from mipsrefs import refs
    for site, kind, addr in refs(data, base, lo, hi): ...   # site = file offset of the lo half / the data word
"""
import struct

LOWS = {0x09: "addiu", 0x0D: "ori", 0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x28: "sb",
        0x29: "sh", 0x2B: "sw"}
NO_RT_DEST = {0, 1, 2, 3, 4, 5, 6, 7, 0x10, 0x12, 0x28, 0x29, 0x2A, 0x2B, 0x2E, 0x32, 0x3A}  # rt not written


def refs(data, base, lo, hi, code=(0, None), window=24):
    """Yield (file_offset, kind, addr) for each reference to an address in [lo, hi).

    base: RAM address of data[0]. code: file range scanned for instructions. A lui's register is tracked for `window`
    instructions (shortcut: no control-flow analysis, so a lui reused across a branch can pair wrongly; insertion
    must check each site's original bytes).
    """
    end = len(data) if code[1] is None else code[1]
    n = (end - code[0]) // 4
    words = struct.unpack_from(f"<{n}I", data, code[0])
    for i, w in enumerate(words):
        if w >> 26 != 0x0F:  # lui
            continue
        rt, hi16 = (w >> 16) & 31, w & 0xFFFF
        for j in range(i + 1, min(i + 1 + window, n)):
            v = words[j]
            op, rs, rt2 = v >> 26, (v >> 21) & 31, (v >> 16) & 31
            if op in LOWS and rs == rt:
                imm = v & 0xFFFF
                addr = (hi16 << 16) | imm if op == 0x0D else ((hi16 << 16) + (imm - 0x10000 if imm & 0x8000 else imm))
                if lo <= addr < hi:
                    yield code[0] + 4 * j, LOWS[op], addr
                if op not in (0x28, 0x29, 0x2B) and rt2 == rt:  # register overwritten
                    break
            elif (op == 0 and (v >> 11) & 31 == rt) or (op not in NO_RT_DEST and rt2 == rt):
                break  # rt redefined by another instruction
    for off in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, off)[0]
        if lo <= v < hi:
            yield off, "word", v


if __name__ == "__main__":
    # lui a0,0x8002; addiu a0,a0,0x1234 ; data word 0x80021234
    prog = struct.pack("<3I", 0x3C048002, 0x24841234, 0x80021234)
    got = list(refs(prog, 0x80020000, 0x80020000, 0x80030000))
    assert got == [(4, "addiu", 0x80021234), (8, "word", 0x80021234)], got
    # negative lo half: lui 0x8003 + addiu -0x10 = 0x8002fff0
    prog = struct.pack("<2I", 0x3C058003, 0x24A5FFF0)
    assert [a for _, _, a in refs(prog, 0, 0x80020000, 0x80030000)] == [0x8002FFF0]
    print("selftest ok")
