"""psxvram.py: render a PS1 VRAM dump (1 MB, 1024x512 16-bit, from L.dump_ppu) to PNG for the graphics survey.

    python -X utf8 tools/psxvram.py ppu_000300.vram.bin OUT_PREFIX [--zoom 2]
Writes OUT_PREFIX.16.png (direct 15-bit colour, 1024x512) and OUT_PREFIX.4.png (every halfword read as four
4-bit indices, grey ramp, 4096x512: texture pages with fonts and UI labels are readable here).
"""
import argparse
import sys

from PIL import Image


def render(vram):
    assert len(vram) >= 1024 * 512 * 2, len(vram)
    vram = vram[:1024 * 512 * 2]  # PCSX-Redux getVRAM returns 2 MB; the second half is 0xFF padding
    rgb = bytearray()
    for i in range(0, len(vram), 2):
        v = vram[i] | vram[i + 1] << 8
        rgb += bytes((((v & 31) * 255) // 31, (((v >> 5) & 31) * 255) // 31, (((v >> 10) & 31) * 255) // 31))
    c16 = Image.frombytes("RGB", (1024, 512), bytes(rgb))
    g4 = bytearray()
    for b in vram:
        g4 += bytes(((b & 15) * 17, (b >> 4) * 17))
    return c16, Image.frombytes("L", (4096, 512), bytes(g4))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vram")
    ap.add_argument("prefix")
    a = ap.parse_args()
    c16, g4 = render(open(a.vram, "rb").read())
    c16.save(a.prefix + ".16.png")
    g4.save(a.prefix + ".4.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
