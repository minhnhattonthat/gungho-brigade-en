# Graphics text survey (phase 1, in progress)

Static sweep: `python -X utf8 tools/timscan.py work/gfx/sweep <files>` (run from work/disc/tree) renders every TIM
into labelled sheets + `index.tsv`. Run 2026-11-21 over TABLE.BIN, MOVIE.BIN, ENDING.BIN, GAMEDATA.DAT,
TABLE/{MENU,OVTABLE,OPENING}.DAT, SCENFILE.DAT, FACE.DAT, MENU.EXE, GUNHO.EXE: 5,493 TIMs, 45 sheets.
No TIMs in GUNHO.EXE, MENU*.EXE, MOVIE.BIN, ENDING.BIN. Skipped: 24-bpp TIMs and images under 16x16 in both
dimensions (printed by the script; GAMEDATA has ~1,000 8x8/12x12 ones that are icons/glyphs - review in a second pass
with `--min 8`).

## Sheets reviewed
| Sheet | Japanese found | Notes |
|---|---|---|
| MENU_DAT_00 (TABLE/MENU.DAT) | +0x18800 `体験版` ("Trial version", 80x32 4bpp) - probably unused in retail; +0x29000 small font 128x132 4bpp has half-width katakana rows (name entry / save font) | logo, title menu, GAME SAVE / TUNE UP / STATUS / NEXT TALE, MOVIE COMMAND, PLAY EP/SP, MOVIE LOAD, EXIT, Now loading: all English already |

## Sheets still to review (next session)
OPENING_DAT_00, OVTABLE_DAT_00, TABLE_BIN_00, GAMEDATA_DAT_00-04, SCENFILE_DAT_00-12, FACE_DAT_00-25 (FACE = 320x240
event stills and 84x82 portraits; check stills for drawn text).

## Seen in game (tour, original disc)
| Screen | Japanese | Source guess |
|---|---|---|
| Battle unit status window (tale 1, work/qa/explore3 f000960) | stat labels, weapon list, unit name | font-drawn (SJIS? glyph list) or GAMEDATA TIMs - VRAM dump in phase 5 |
| Battle command menu (small box, tale 1) | command icons/labels | GAMEDATA small TIMs? |
| Unit name plate under portrait (`ジャック`?) | katakana name | unknown |
| Tutorial message box | SCENFILE text (font-drawn) | text, not graphics |
