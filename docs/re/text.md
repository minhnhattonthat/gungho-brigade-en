# Text: encoding, files, pointers

Disc: SLPS-01902, one MODE2/2352 track, ISO9660. `dumpsxiso -x tree -s layout.xml` unpacks it (work/disc/).
No earlier fan patch found (web search 2026-11-21: only ROM/database pages). The logo, title menu
(NEW GAME / CONTINUE / GAME LOAD), "Now loading..." and chapter cards ("tale 1 THE YOUNG GUNS") are already English.

## Encoding
- Shift-JIS (cp932), NUL-terminated. **verified**: the tutorial box in tale 1 shows SCENFILE entry 0 string +0xe4
  ("ユニットを、赤く表示された領域へ移動する...") and RAM holds those exact bytes at 0x80159254 (work/qa/ram2).
- Line break: `/` (0x2F) in most strings, `\n` (0x0A) in some. Leading spaces (0x20) indent. **guess** from layout:
  `審判/「...` puts the speaker name on its own line before the quote.
- Strings start 4-byte aligned, padded with 0x00. **verified** on SCENFILE entries 0 and 15.
- The big font covers only a fixed glyph list: GUNHO.EXE file +0x5db78 (RAM 0x8007d378), 1376 (0x560) SJIS
  characters, order = glyph index. **verified** (read watch, work/qa/watch2): TABLE.BIN code byte-swaps the list once
  (0x801607f4) and binary-searches it per character (0x8015fa54, called from 0x801612f8); index*22 = offset into a
  1bpp **11x11** bitmap font (2 bytes/row, 11 rows) whose RAM pointer is at 0x800a1af0. Rendering glyph 603 gives
  左 (matches the list). Bitmap copies (identical start): GAMEDATA.DAT +0x346800, TABLE/MENU.DAT +0x30aec,
  TABLE/OVTABLE.DAT +0x2ec (30,272 bytes each). Full-width Latin present only partly (A-I K-P S-U W X, a c d e g h i
  k l m n o p r s t u w z): English needs glyphs added or a VWF (phase 5).
- **Second encoding: half-width katakana + ASCII (cp932 single bytes)** for unit, pilot, weapon, ability and part
  names and battle messages (`%d ﾉ ﾀﾞﾒｰｼﾞ`, `ﾘｶﾊﾞｰ` = D8 B6 CA DE B0, dakuten as a separate DE byte). **verified**:
  the status window shows ビズリィ / リョウテキキ / クイック / リカバー; those exact cp932 strings are in GUNHO.EXE
  (e.g. ﾘｶﾊﾞｰ, ｸｲｯｸ at file 0x82100-0x82300). Drawn with the small 8x12 font (GAMEDATA entry 265 +0x3274, see
  graphics.md), laid out in JIS X 0201 order (row 0x30 = 0-9:, 0x40 = ㎜A-O, 0x50 = P-Z, 0x60/0x70 = a-z,
  0xA0-0xDF = half-width kana; 0x80-0x9F and 0xE0 rows hold precomposed ガ..ボ, パ..ポ). The small font already has
  A-Z a-z 0-9, so English names need no font work (punctuation other than `:` and `ー` is missing).
  Earlier "not stored as SJIS" result was a full-width-only search.
- Battle help line (bottom of the status window, e.g. 左手に、ランダル...): TABLE.BIN 0x801617b8 turns the string into
  u16 SJIS cells, **single-byte characters become a full-width space**, max 0x62/2 = 49 cells at 12 px pitch up to
  x=320 (26 visible), then draws with 0x80161080. ASCII there needs a code patch (phase 5).

## Files (LEN = little-endian u32 start offsets into the matching DAT, no end entry)
| File | Size | Text | Notes |
|---|---|---|---|
| SCENFILE.DAT/.LEN | 7.3 MB, 177 entries | ~2250 strings, ~111 KB | story, objectives, tutorials. See below |
| GUNHO.EXE | 534 KB, load 0x80020000 (addr = 0x80020000 + off - 0x800) | 26 SJIS strings 0x1f30-0x238e; ~200 half-width strings 0x824-0x82230 | skill/ability descriptions (SJIS); battle messages, weapon/unit names 0x1dbc-0x1f30, pilot records 0x777ec+ stride 0x120 (name first), part/ability names 0x82000-0x82230; glyph list at 0x5db78 |
| MENU.EXE | 208 KB, load 0x80020000 | 17 strings | file/memory-card errors (0x80c-), memory-card messages 0x2cf5c- |
| SLPS_019.02 / MENUMV.EXE | 168 KB each | 16 strings | boot exe, error messages; MENUMV is a near-twin |
| TABLE.BIN | 94 KB, loaded at 0x8015eed0 in battle (verified, RAM) | 27 SJIS strings 0x14-0x11c2e + half-width names (ｶｸﾄｳ ｼﾞﾒﾝ ﾄﾚｰﾗｰ at 0x168-0x188) | battle module: code (font draw, menus) + data; save/memory-card messages |
| ENDING.BIN | 18 KB | credits 0x2970-0x32f4 | staff roll, `役職：名前` |
| LEMENU*.EXE, MOVIE.BIN, WPMOTION, BTMOTION | | none | |
| GAMEDATA.DAT, TABLE/*.DAT, FACE.DAT | | images only (TIM) | see graphics.md |
| MOVIE/*.STR, MOVIE2/*.STR, XA/*.XA | | FMV + voice | FMVs seen in the opening have no on-screen text; voiced. Subtitles out of scope unless the story needs them (phase 8 note) |

Unit/weapon/ability names are half-width cp932 strings (see Encoding). The battle command menu labels (射撃 格闘 ...)
are TIM graphics (graphics.md). Status-window labels (Pilot, Level, Gunshot ...) are English TIM graphics already.
Scan for half-width strings: 4-aligned, NUL-bounded, >=3 kana, >=70% kana; real hits only in GUNHO.EXE and
TABLE.BIN (other files: image-data noise). Exact list by pointer in phase 4.

## SCENFILE text overlays (pointer format)
- Each stage's text lives in an overlay that loads at **0x80159170** (verified for tale 1 = SCENFILE entry 0, RAM
  dump work/qa/ram2/ram_000300.bin). Layout: `u32 count` · NUL-terminated SJIS strings (4-aligned) · MIPS code (the
  stage's event script, calling GUNHO.EXE routines) · **table of absolute u32 string pointers (0x8015xxxx)** at the end.
  Entry 0: table at file +0x6b0, 8 pointers, first = 0x80159174 (charset string), then +0x78, +0x9c, +0xe4 ...
- Code inside the overlay also refers to the table / strings by absolute address (lui/addiu): moving code is unsafe;
  rewrite strings + table, keep code bytes or relocate them with every lui/addiu fixed. **guess**.
- LEN boundaries do not match logical overlays: text-bearing entries (15, 22, 29, 36, 43, 49, 56, 63, 69, 70, 77, 84,
  85, 92, 99, 104, 105, 106, 152-158, 161-165, 169-171, 174, 175) carry a pointer table whose implied load base is
  0x8015xxxx minus 0x0-0x780 bytes, i.e. the overlay starts partway into the entry (e.g. entry 15: overlay at entry
  +0x780 if it loads at 0x80159170; the bytes before are height-map data). Exact split per entry: phase 4 work.
- Load buffer size: TABLE.BIN sits at 0x8015eed0, so a text overlay has at most 0x5d60 bytes (23,904) unless it
  ends before TABLE.BIN loads. **guess**; measure the largest overlay (entry 164, 25,132 bytes incl. prefix) in phase 4.

## Free space
- Disc: files are opened by ISO name, not hard-coded LBA: SLPS_019.02 and MENU.EXE carry `cdrom:%s;1` (CdSearchFile
  format) with the bare names (OPENING.DAT, MENU.EXE, GUNHO.EXE ...); GUNHO.EXE lists TABLE.BIN, SCENFILE.DAT,
  GAMEDATA.DAT, BTMOTION/WPMOTION.DAT, FACE.DAT/LEN, MOVIE.BIN, ENDING.BIN and `\XA\XA0nn.XA;1`. **Verified** 2026-11-21: GUNHO.EXE padded by
  4 KB (every later file moved 2 sectors) still warps to the stage 8 battle, the intermission and the staff roll. Inside each DAT, entries are addressed by
  the LEN offset table, so a grown entry needs the LEN rewritten.
- RAM: unknown; overlay buffer bound above.
