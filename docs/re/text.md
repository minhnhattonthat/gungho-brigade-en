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

## Font (phase 5): digraph glyphs, no code change
- Two 11x11 SJIS fonts, each = sorted code list (binary search, index = glyph) + 1bpp bitmap (22 bytes/glyph, u16
  BE rows, MSB = column 0), drawn at a 12-px pitch, white, no shadow:
  GUNHO font: list GUNHO.EXE 0x5db78 (1376) -> bitmap GAMEDATA.DAT 0x346800 (stages, battle, intermission).
  Menu font: list MENU.EXE 0x2c59c (1175) -> bitmap TABLE/MENU.DAT 0x30800 and TABLE/OVTABLE.DAT 0x0 (same bytes).
- English = **digraphs**: tools/digraph.py redraws kana/kanji glyphs (codes >= 0x829F) as two 5-px letters
  (fonts/font5.txt) at columns 0-4 / 6-10. Codes present in both lists (1040) are used first, so text in TABLE.BIN /
  MENU.EXE / SLPS / MENUMV gets pairs valid in either font; 336 GUNHO-only codes are overflow for other text.
  Codes below 0x829F (punctuation, fullwidth digits/Latin) stay: runtime text uses them.
- A single **0x20 byte advances half a cell (6 px)** in dialogue: **verified** (marker build, s08: "The quick brown
  fox" spaces land on the 6-px grid). So words start on any half cell; a pair holds a space only after an odd-length
  word. Effective pitch: 6 px per character, 1 byte per character.
- `...` is drawn as one 5-px glyph `…` (fonts/font5.txt, tools/digraph.py `pairs`): 2 bytes saved per ellipsis.
- **Staff roll (ENDING.BIN) can't draw on a half cell:** a glyph after a lone 0x20 (i.e. after an even-length word)
  shows as coloured noise (e34, verified 2026-11-22; the marker build's "0x88e6" case was the same). Ending text is
  encoded `aligned` (tools/digraph.py: spaces paired like letters, " K"), so every glyph sits on a 12-px cell.
- ENDING.BIN staff roll longer than its slot: appended at the 4-aligned file end and its one reference (`addiu` at
  file 0x1584, lui half unchanged) repointed (`extract.write_back`); ENDING.BIN code refers to nothing past its end.
- `%` in dialogue is a literal (the overlay text is not printf'd; **guess**, only `%s`/`%d` in EXE strings are args).
- Half-width rows (unit/weapon/pilot names, battle messages; small 8x12 font) are written as plain ASCII.
- tools/insert.py writes every row (`en`, or `--marker`, or `--qa ID=TEXT`) plus the three font copies into
  work/build/files/; in place only for now (phase 7 relocates strings that outgrow their slot).

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
  dump work/qa/ram2/ram_000300.bin). Layout: `u32 stage id + 4` · NUL-terminated SJIS strings (4-aligned) · MIPS code (the
  stage's event script, calling GUNHO.EXE routines) · **table of absolute u32 string pointers (0x8015xxxx)** at the end.
  Entry 0: table at file +0x6b0, 8 pointers, first = 0x80159174 (charset string), then +0x78, +0x9c, +0xe4 ...
- Code inside the overlay also refers to the table / strings by absolute address (lui/addiu): moving code is unsafe;
  rewrite strings + table, keep code bytes or relocate them with every lui/addiu fixed. **guess**.
- LEN boundaries do not match logical overlays: text-bearing entries (15, 22, 29, 36, 43, 49, 56, 63, 69, 70, 77, 84,
  85, 92, 99, 104, 105, 106, 152-158, 161-165, 169-171, 174, 175) carry a pointer table whose implied load base is
  0x8015xxxx minus 0x0-0x780 bytes, i.e. the overlay starts partway into the entry (e.g. entry 15: overlay at entry
  +0x780 if it loads at 0x80159170; the bytes before are height-map data).
- **Phase 4 (verified statically, tests/test_extract.py):** the overlay offset per entry is `OVERLAYS` in
  tools/extract.py. The first u32 is not a count but the **stage id + 4** (4..39 = stages 0-35, one overlay each, 36
  in all). Every pointer-table target starts right after a NUL; strings fill [+4, text end) with only zero padding
  between them. After the text: data strings the code reaches by lui/addiu (OBJECT_R, OBJECT_L, \MOVIE\Snn), then
  code, then the table at the very end. Entry 106 = a copy of entry 104's pointer table with code, no strings (not an
  overlay). Stage 0 slot 0 (+0x4) is a fullwidth A-z charset list, left as data. Overlays hold no half-width kana.
- Stale text copies: entries 17, 24, 31, 38, 45, 51, 58, 65, 79, 87, 107, 167 start with byte copies of lines from the
  previous stage overlay, breaking off into binary mid-string (buffer residue). Not extracted. **guess** that nothing
  reads them; the marker build (phase 5) will show any box still in Japanese.
- **Growing an overlay (verified 2026-11-22, marker builds + warps):** an overlay may grow at its end (= its LEN
  entry's end, after the pointer table) by **whole 0x800 sectors**, with every later LEN offset shifted: s14 with its
  whole text moved past the table showed s14_0004, s35 padded, and the shifted s29 all load. Growth by any other
  amount (0x9f8, 0xeb4) hangs at "Now loading" for the grown stage AND for later, merely shifted stages (s29).
  `extract.write_back` does this (strings that don't fit the region go to the tail); tools/fitcheck.py checks the
  0x5d60 bound.
- Load buffer size: TABLE.BIN sits at 0x8015eed0, so a text overlay has at most 0x5d60 bytes (23,904) unless it
  ends before TABLE.BIN loads. **guess**; measure the largest overlay (entry 164, 25,132 bytes incl. prefix) in phase 4.

## Extraction (phase 4)
`python -X utf8 tools/extract.py` writes `script/*.tsv` (id, max, jp, en, notes; never overwrites without `--force`):
36 `scen_sNN.tsv` (2228 lines), `gunho` (135: battle messages, weapon/unit/ability names, ability descriptions),
`pilots` (123 records at GUNHO.EXE 0x776fc, stride 0x30, 16-byte name field), `table` (33), `menu` (15), `slps` and
`menumv` (15 each; dev-version notice + file errors), `ending` (149 staff-roll lines, blob at ENDING.BIN 0x2970).
EXE strings are found by references (tools/mipsrefs.py: lui + addiu/ori/load/store pairs, u32 words) into each file's
text ranges (`EXES` in extract.py); several strings are reached only through u32 pointer tables right before them.
Codec: tools/sjis.py (cp932 as a tbl.Table, `0x0A` = `{n}`). `max` = in-place bytes (slot to the next string, NUL
excluded; EXE slots end at the 4-aligned NUL padding because zero words after it may be variables).
Tests: codec roundtrip, write-back of every jp string reproduces each file, overlay sanity, TSV in sync with the disc,
and coverage: no 4-aligned Japanese-looking run anywhere on the disc (except FMV/XA/sound) outside extracted strings
or the listed non-text (glyph lists, ASCII->fullwidth tables, stale copies).

## Free space
- Disc: files are opened by ISO name, not hard-coded LBA: SLPS_019.02 and MENU.EXE carry `cdrom:%s;1` (CdSearchFile
  format) with the bare names (OPENING.DAT, MENU.EXE, GUNHO.EXE ...); GUNHO.EXE lists TABLE.BIN, SCENFILE.DAT,
  GAMEDATA.DAT, BTMOTION/WPMOTION.DAT, FACE.DAT/LEN, MOVIE.BIN, ENDING.BIN and `\XA\XA0nn.XA;1`. **Verified** 2026-11-21: GUNHO.EXE padded by
  4 KB (every later file moved 2 sectors) still warps to the stage 8 battle, the intermission and the staff roll. Inside each DAT, entries are addressed by
  the LEN offset table, so a grown entry needs the LEN rewritten.
- RAM: unknown; overlay buffer bound above.
