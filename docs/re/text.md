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
- The font covers only a fixed glyph list: GUNHO.EXE file +0x5db78, 1376 SJIS characters (2752 bytes, ends before
  `88 13 00 00`), order = glyph index. **guess** (looks like a charset table; draw-call not hooked yet). Full-width
  Latin present only partly (A-I K-P S-U W X, a c d e g h i k l m n o p r s t u w z): English needs a font/VWF change
  (phase 5).

## Files (LEN = little-endian u32 start offsets into the matching DAT, no end entry)
| File | Size | Text | Notes |
|---|---|---|---|
| SCENFILE.DAT/.LEN | 7.3 MB, 177 entries | ~2250 strings, ~111 KB | story, objectives, tutorials. See below |
| GUNHO.EXE | 534 KB, load 0x80020000 (addr = 0x80020000 + off - 0x800) | 26 strings 0x1f30-0x238e | skill/ability descriptions; glyph list at 0x5db78 |
| MENU.EXE | 208 KB, load 0x80020000 | 17 strings | file/memory-card errors (0x80c-), memory-card messages 0x2cf5c- |
| SLPS_019.02 / MENUMV.EXE | 168 KB each | 16 strings | boot exe, error messages; MENUMV is a near-twin |
| TABLE.BIN | 94 KB, loaded at 0x8015eed0 in battle (verified, RAM) | 27 strings 0x14-0x11c2e | save/memory-card messages |
| ENDING.BIN | 18 KB | credits 0x2970-0x32f4 | staff roll, `役職：名前` |
| LEMENU*.EXE, MOVIE.BIN, WPMOTION, BTMOTION | | none | |
| GAMEDATA.DAT, TABLE/*.DAT, FACE.DAT | | images only (TIM) | see graphics.md |
| MOVIE/*.STR, MOVIE2/*.STR, XA/*.XA | | FMV + voice | FMVs seen in the opening have no on-screen text; voiced. Subtitles out of scope unless the story needs them (phase 8 note) |

Unit names, weapon names and menu labels (ラグボール in menus, ヒダリウデ, status window labels) are NOT stored as
SJIS anywhere outside SCENFILE story text, nor as glyph-index strings (searched u8/u16 index encodings of 5 words):
they are drawn from TIM graphics (graphics.md). **guess**, to confirm by VRAM dump in phase 5.

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
- Disc: rebuilding with mkpsxiso lets files grow (LBAs move; the game reads by ISO name? unverified - check whether
  the EXE has hard-coded LBAs before growing any file; identity build in phase 3).
- RAM: unknown; overlay buffer bound above.
