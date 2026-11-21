# Window data: text budgets per box variant (width gate, phase 5)

Measured on the marker build (`python -X utf8 tools/insert.py --marker` + build.py) unless marked **guess**.
"char" = one English letter as encoded by tools/insert.py: digraph rows 6 px per char (a word-separating space is
one 0x20 byte = 6 px), fullwidth rows 12 px per char, small-font rows ~8 px per char.

| Variant | Encoding | Budget | Evidence |
|---|---|---|---|
| Dialogue box (scen_*, speaker line + text) | pair | **42 chars/line, 3 lines** incl. the speaker line; a 4th line falls below the frame (y=216 vs frame 217) | frame x 26..291, text x=34, lines y 174/188/202; ruler line ran past the frame unclipped (work/qa/wg1/f000120.png). Last char fully inside: #42 ends x=284 |
| Tutorial box (top, s00) and objective boxes (勝利条件/敗北条件, top/bottom, 1-3 lines) | pair | **42 chars/line**, 3 lines | same frame x 26..291, text x=34/35 (work/qa/warp/s00/final.png, work/qa/bt2/f002208.png) |
| Battle/status help line (gunho_* SJIS rows: skill/ability descriptions) | pair | **50 chars**, 1 line (**guess** for the right end: text x=16, screen edge 320; engine limit 49 u16 cells = 98 chars) | work/qa/warp/i08_status/final.png |
| Memory-card messages (table_*, menu_*: title GAME LOAD, intermission GAME SAVE) | full | **18 chars/line** keeps inside the window frame (x 48..272); 24 = band edge; lines centred; up to 5 lines with `{n}` | work/qa/sv2/f000100.png, work/qa/tl2 |
| Skill name in STATUS (small font) | small | **10 chars** (x 42, level number at x 126, 8 px/char) | i08_status final |
| Pilot name in STATUS header | small | **7 chars** (x 125, "SP" at x 185) | i08_status final |
| Pilot / unit / weapon names in battle windows | small | **not measured** | phase 5 todo |
| Battle messages (`%d ﾉ ﾀﾞﾒｰｼﾞ` etc., small font) | small | **not measured** | phase 5 todo |
| Staff roll (ending_*) | pair | **not measured** (marker shows, work/qa/warp/e34) | phase 5 todo |
| table_00430 / table_00440 (○戦闘シーン / 短縮) | full | **not seen yet** | phase 5 todo |

Notes
- JP lines peak at 42 half-cells (707 strings); 7 strings reach 44 (they overflow in Japanese too).
- Boxes resize to the line count (objectives 1 line, tutorial 3).
- Save titles table_11800/11844/11ac4 (BIOS card manager, digits written at fixed offsets) are not markered.
