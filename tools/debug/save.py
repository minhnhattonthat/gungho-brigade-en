"""Gungho Brigade memory-card save editor (layout: tools/debug/save_layout.md).

    python -X utf8 tools/debug/save.py CARD.mcd --show
    python -X utf8 tools/debug/save.py CARD.mcd --out NEW.mcd [--stage N] [--poke OFF:SIZE=VAL ..]

Edits the first BISLPS-01902 save on the card, starting from a game-written file (never from zeros), and fixes
both checksums. OFF is an offset into the game-state block (RAM 0x80010000, saved at data +0x108), SIZE 1/2/4.
The PS1 directory frame is not touched (same size, same name), so its XOR byte stays valid.
"""
import argparse
import struct
import sys

STATE = 0x108   # save data offset of the state block (RAM 0x80010000)


def find_save(card):
    for i in range(1, 16):
        e = card[i * 128:(i + 1) * 128]
        if e[0] == 0x51 and e[10:22] == b"BISLPS-01902":
            return i * 0x2000
    raise SystemExit("no Gungho Brigade save on this card")


def checksums(blk):
    """(+0x100, +0x104): bytes of the header/icon + 8 state bytes, and bytes of everything from +0x108
    (verified against two game-written saves; game check: TABLE.BIN 0x8016a740)."""
    return (sum(blk[:0x100]) + sum(blk[0x108:0x110])) & 0xFFFFFFFF, sum(blk[0x108:0x2000]) & 0xFFFFFFFF


def show(blk):
    c100, c104 = struct.unpack_from("<II", blk, 0x100)
    title = blk[4:68].split(b"\0")[0].decode("cp932", "replace")
    stage, frames = struct.unpack_from("<hI", blk, STATE)[0], struct.unpack_from("<I", blk, STATE + 4)[0]
    ok = (c100, c104) == checksums(blk)
    print(f"title: {title}\nstage: {stage}\nplay time: {frames} ({frames // 3600} min at 60 fps)\n"
          f"checksums: {c100:#x} {c104:#x} ({'ok' if ok else 'BAD'})")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("card")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--stage", type=int)
    ap.add_argument("--poke", action="append", default=[], help="OFF:SIZE=VAL into the state block (hex ok)")
    a = ap.parse_args(argv)
    card = bytearray(open(a.card, "rb").read())
    assert len(card) == 0x20000, "not a 128 KB PS1 memory card image"
    base = find_save(card)
    blk = card[base:base + 0x2000]
    if a.show or not a.out:
        return 0 if show(blk) else 1
    if a.stage is not None:
        assert 0 <= a.stage <= 35, "stage index 0..35 (tools/debug/scenes.tsv)"
        struct.pack_into("<h", blk, STATE, a.stage)
    for p in a.poke:
        off, rest = p.split(":")
        size, val = rest.split("=")
        off, size, val = int(off, 0), int(size), int(val, 0)
        assert size in (1, 2, 4) and 0 <= off and STATE + off + size <= 0x2000, f"bad poke {p}"
        blk[STATE + off:STATE + off + size] = val.to_bytes(size, "little")
    struct.pack_into("<II", blk, 0x100, *checksums(blk))
    card[base:base + 0x2000] = blk
    open(a.out, "wb").write(card)
    show(blk)
    return 0


if __name__ == "__main__":
    sys.exit(main())
