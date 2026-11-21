# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build (not started). Phase 2 debug tool done 2026-11-21. Last build: none yet (warps run on
  the original disc).
- **Done:**
  - Step 0 + phase 1 (recon, graphics survey): see git history, `docs/re/`.
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
- **Next (phase 3):** identity build: `work/disc/tree` + `work/disc/layout.xml` already exist (dumpsxiso run in
  phase 1); write `build.py` (check_rom, dumpsxiso if tree missing, mkpsxiso -y with cwd tree/, output
  build/gungho_en.bin/.cue) and a slow test that the unedited rebuild is byte-identical to `rom.sha1`; then a rebuild
  that moves LBAs (pad a file) still warps to a battle (`warp.py s08 --cue build/...`).
- **Notes:** stage index != tale number (stage 8 shows "tale 7"); event stages 3/11/32 chain into the next stage.
  The portable card tools/pcsx/memcard1.mcd must stay blank (warp.py always passes a blank `--sav`). Game over warp
  shows over the loading screen (battle view never drawn) and only the first leader's line; stage 0 has no defeat
  handler.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
