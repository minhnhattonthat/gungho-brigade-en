# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build (in progress: font done, marker build boots, width gate partly
  measured). Last build: build/gungho_en.bin 2026-11-22 = marker build (`tools/insert.py --marker` + build.py).
- **Done:**
  - Phase 5 so far (2026-11-22): **font = digraphs, no code change** (tools/digraph.py, fonts/font5.txt; details
    docs/re/text.md §Font). Dialogue/battle text = pairs of 5-px letters in kana/kanji slots, 0x20 = 6-px space.
    MENU.EXE/SLPS/MENUMV/TABLE.BIN text = fullwidth Latin (their font is keyed by the real SJIS code; pairs showed as
    kana there). Small-font rows = ASCII. `tools/insert.py [--marker] [--qa ID=TEXT]` writes work/build/files/
    (rerun before build.py). tests/test_insert.py. `warp.py --all --cue build/gungho_en.cue` on the marker build:
    46/46 arrive, every dialogue/objective/tutorial box, help line, credits and memory-card message seen shows its
    marker (work/qa/warp/sheet*.png). Budgets: docs/windows.md (dialogue/tutorial/objective 42 chars x 3 lines).
  - Phase 4 (2026-11-21): `tools/extract.py` -> 43 `script/*.tsv` (2713 rows: 36 stage overlays 2228, gunho 135,
    pilots 123, ending 149, table 33, menu/slps/menumv 15 each), codec `tools/sjis.py` (cp932 tbl), refs scanner
    `tools/mipsrefs.py`, `extract.write_back()` (in-place, NUL-padded; insert base for phase 5/7).
    `tests/test_extract.py`: roundtrip, write-back identity, overlay sanity, TSV sync, disc-wide coverage. Details and
    formats: `docs/re/text.md` §SCENFILE text overlays, §Extraction.
  - Step 0 + phase 1 (recon, graphics survey): see git history, `docs/re/`.
  - Phase 3 (2026-11-21): `build.py` (check_rom, dumpsxiso if work/disc missing, mkpsxiso on a copy of layout.xml
    with absolute paths; any file under the overlay `work/build/files/<disc path>` replaces the tree file, unknown
    overlay paths refused). `tests/test_build.py`: slow test rebuild == rom.sha1 (passes), fast overlay tests.
    LBA move proven: GUNHO.EXE +4 KB in the overlay still warps to s08 battle, i08 intermission, e34 staff roll
    (files found by name; `docs/re/text.md` §Free space).
  - Phase 2 (2026-11-21): `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` warp from a cold boot to all 36 stages
    (intro, tale card, battle start), the intermission menu (GAME SAVE / TUNE UP / STATUS / NEXT TALE), the staff
    roll (e34, s35), the title menu and title GAME LOAD, and game over (go08: stage 8 leader's defeat line;
    go08_over: FACE 106 "Game over" image); states in work/states/ (`warp.py --all` regenerates; proof shots
    work/qa/warp/<scene>/final.png + work/qa/warp/sheet*.png). `warp.py --all` passed 2026-11-21 (all 46 scenes).
  - `tools/debug/save.py` (layout + both checksums in `tools/debug/save_layout.md`, test tests/test_save.py):
    game-written intermission save work/saves/i08_saved.mcd edited to stage 20 loads via GAME LOAD with no error and
    NEXT TALE starts stage 20 (work/qa/load2). Fixture regen: `warp.py i08`, then emu.py --state-in
    work/states/i08.sstate --sav work/saves/blank.mcd --route-str "6 circle;400 -;6 circle;300 -;6 circle;300 -;6
    circle;300 -;6 circle;2000 -" and copy <out>/memcard1.mcd.
  - Game flow RE: `docs/re/debug.md` (exe chain, state block, stage table, event runner + args, stage-end calls,
    defeat handler).
- **Next (phase 5, to finish):** measure the `not measured` rows of docs/windows.md: battle windows (pilot/unit/
  weapon names, small-font battle messages; battle controls: square on a unit opens its portrait+stats, circle did
  nothing on the map, work/qa/bt2), staff roll width (e34), table_00430/00440, help line right end (`--qa` a 60-char
  gunho row). Glyph torture line: s08 test rows 07e8/0870/08f0 are never shown in the s08 intro (event skips them),
  put `--qa` torture text on s08_078c instead (max 91). Then phase 5 done -> translator brief limits from
  docs/windows.md. Phase 7 concern: English often outgrows in-place slots (overlay buffer bound 0x5d60 still a guess;
  EXE strings repoint via mipsrefs sites); digraph capacity 1376-75 codes (marker uses ~300 pairs).
  Stale SCENFILE copies: no Japanese seen in the 46-scene marker tour.
- **Notes:** stage index != tale number (stage 8 shows "tale 7"); event stages 3/11/32 chain into the next stage.
  The portable card tools/pcsx/memcard1.mcd must stay blank (warp.py always passes a blank `--sav`). Game over warp
  shows over the loading screen (battle view never drawn) and only the first leader's line; stage 0 has no defeat
  handler.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
