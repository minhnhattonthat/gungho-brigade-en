from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rom_sha1_listing_is_filled():
    text = (ROOT / "rom.sha1").read_text(encoding="utf-8")
    assert "<sha1>" not in text and "Gungho Brigade (Japan).bin" in text
