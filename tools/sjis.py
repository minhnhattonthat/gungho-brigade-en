"""Shift-JIS (cp932) as a tbl.Table: every single byte and double-byte code cp932 decodes, plus `0A={n}` (the game's
second line break; `/` is the usual one). Bytes cp932 can't decode, tabs and other control bytes come out as `[XX]`.

    from sjis import SJIS
    text, n = SJIS.decode(data, pos, length)   # length = string bytes without the NUL
"""
from tbl import Table


def _lines():
    yield "0A={n}"
    for b in list(range(0x20, 0x7F)) + list(range(0xA1, 0xE0)):
        yield f"{b:02X}=" + ("\\s" if b == 0x20 else bytes([b]).decode("cp932"))
    for lead in list(range(0x81, 0xA0)) + list(range(0xE0, 0xFD)):
        for trail in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                ch = bytes([lead, trail]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if ch in "{}[]":  # never: fullwidth forms differ, but keep the token syntax unambiguous
                continue
            yield f"{lead:02X}{trail:02X}={ch}"


SJIS = Table(list(_lines()))

if __name__ == "__main__":
    raw = "目的：赤く/ﾘｶﾊﾞｰ %d".encode("cp932") + b"\n\x09\x80"
    text, n = SJIS.decode(raw, 0, len(raw))
    assert text == "目的：赤く/ﾘｶﾊﾞｰ %d{n}[09][80]" and SJIS.encode(text) == raw, text
    # cp932 duplicates (NEC/IBM rows) decode to the same char; the non-canonical code must stay [XX][YY]
    dup = bytes.fromhex("FA40")  # IBM ⅰ, also at EEEF
    assert SJIS.encode(SJIS.decode(dup, 0, 2)[0]) == dup
    print("selftest ok")
