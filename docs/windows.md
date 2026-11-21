# Window data: text budgets per box variant (width gate, phase 5)

Measured on the marker build (`python -X utf8 tools/insert.py --marker` + build.py) unless marked **guess**; "ruler
build" = `python -X utf8 tools/ruler.py gunho_ pilot_ ending_002 table_0043 table_0044` + build.py (slot-max
"123456789A..." text; ENDING.BIN has room for only one 64-char ruler line next to the markers).
"char" = one English letter as encoded by tools/insert.py: digraph rows 6 px per char (a word-separating space is
one 0x20 byte = 6 px), fullwidth rows 12 px per char, small-font rows ~8 px per char.

| Variant | Encoding | Budget | Evidence |
|---|---|---|---|
| Dialogue box (scen_*, speaker line + text) | pair | **42 chars/line, 3 lines** incl. the speaker line; a 4th line falls below the frame (y=216 vs frame 217) | frame x 26..291, text x=34, lines y 174/188/202; ruler line ran past the frame unclipped (work/qa/wg1/f000120.png). Last char fully inside: #42 ends x=284 |
| Tutorial box (top, s00) and objective boxes (勝利条件/敗北条件, top/bottom, 1-3 lines) | pair | **42 chars/line**, 3 lines | same frame x 26..291, text x=34/35 (work/qa/warp/s00/final.png, work/qa/bt2/f002208.png) |
| Battle/status help line (gunho_* SJIS rows: skill/ability descriptions) | pair | **50 chars**, 1 line (text x=16, screen edge 320; engine limit 49 u16 cells = 98 chars). Ruler: 46 chars drawn clean to x~290 (in-place slots max 47 bytes) | ruler build: work/play/bt/0028.png, work/qa/warp/i08_status/final.png |
| Memory-card messages (table_*, menu_*: title GAME LOAD, intermission GAME SAVE) | full | **18 chars/line** keeps inside the window frame (x 48..272); 24 = band edge; lines centred; up to 5 lines with `{n}` | work/qa/sv2/f000100.png, work/qa/tl2 |
| Small font, all rows below | small | **6 px per char since phase 7** (tools/smallfont.py; was 8). Budgets = `NAME_BUDGET` in tools/batches.py, or the JP's own width (8 px per cell) when wider | 8-px measurements kept in brackets |
| Skill name in STATUS (small font) | small | **13 chars** (x 42, level number at x 126: 84 px) [10 at 8 px] | i08_status final |
| Pilot name in STATUS header | small | **14 chars** measured (centred as 8 px/char: start 148 - 4n, ink to 148 + 2n; portrait left, "SP" at x 185); budget **12** for the battle status window | ruler build 2026-11-22, work/qa/warp/i08_status |
| Unit name in the battle hover box (portrait + name + HP, select/hover on a unit) | small | **10 chars**; the 11th touches the frame [8 at 8 px] | ruler build 2026-11-22: s01 + `60 -;6 circle;90 -;6 circle;90 -` |
| Weapon list (shoot command: name rows over Power/Range/Hit) | small | **12 chars** from the 8-px result (9 clean = 72 px, 10th touched the frame) **guess** until measured at 6 px | work/play/bt/0009.png |
| Unit name in TUNE UP header | small | room to x~125 (~18 chars at 6 px); the hover box is the binding window for unit names | work/qa/warp/i08_tune/final.png |
| Pilot name in the battle status window | small | **12 chars**: at 8 px a 13-char ruler started clear of the portrait and only ran over the HP value on the right; centred, 12 at 6 px reaches less far right than 7 did at 8 px | work/play/bt/0028.png |
| Skill name, battle status window | small | **13 chars** (10 at 8 px = 80 px, the 11th ran into the level number) | work/play/bt/0028.png |
| Battle messages (gunho_00824 `%d ﾉ ﾀﾞﾒｰｼﾞ`, 00834 `ｿｼﾃ ﾊｽﾞﾚﾀ`, 00840 `%s ﾃﾞｺｳｹﾞｷｼﾃ`) | small | **never shown**: debug leftovers, sprintf'd into stack buffers nothing reads (0x8002a1a0 / 0x8002ab10, docs/re/debug.md). Budget = slot only (15/11/15 bytes); keep `%d`/`%s` | execution phase played twice (full and shortened scenes, work/play/bt 0044, callers.lua log): sprintf fires, no text on screen |
| Staff roll (ending_*) | pair | **32 chars** (16 cells of 12 px, the JP's widest line). The screen shows 48, but each line is drawn into a VRAM strip at x 320..511 and a longer one spills past x 512 into the picture texture: garbage over the "System Programming" still and old roll text in place of the last picture (phase 8 VRAM dumps EN vs JP at f13860). Longer rows take `{n}` = another roll line; extract.write_back drops as many trailing blank lines, so the roll keeps 301 lines | ruler build e34 f004800 (screen); work/qa/roll/vram_en vs vram_jp |
| table_00430 (○戦闘シーン, config option label) | full | **6 chars** clean (x=60, 12 px/char); the system-menu icon column stays drawn on top of the window from x~134, so a 7th char runs under it (in-place slot max 7); window frame x 41..274 | ruler build, work/play/bt/0042.png (battle: circle on empty ground -> system menu -> pad icon) |
| table_00440 (短縮, option value button next to ON/OFF) | full | **4 chars** inside the button (x 79..134); slot max 3 in place | same shot |
| Glyph check, dialogue | pair | all 5-px glyphs (A-Z a-z 0-9 punctuation) and odd/even pair alignment draw clean | work/qa/torture/glyphs.png (`--qa` on s08_0140/049c/0748) |

Notes
- JP lines peak at 42 half-cells (707 strings); 7 strings reach 44 (they overflow in Japanese too).
- Boxes resize to the line count (objectives 1 line, tutorial 3).
- Save titles table_11800/11844/11ac4 (BIOS card manager, digits written at fixed offsets) are not markered.
