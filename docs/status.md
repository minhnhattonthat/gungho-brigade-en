# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (nearly done: every scene in tools/debug/scenes.tsv warps from a cold boot; game over
  scene still missing). Last build: none yet (warps run on the original disc).
- **Done:**
  - Step 0 + phase 1 (recon, graphics survey): see git history, `docs/re/`.
  - Phase 2 (2026-11-21): `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` warp from a cold boot to all 36 stages
    (intro, tale card, battle start), the intermission menu (GAME SAVE / TUNE UP / STATUS / NEXT TALE), the staff
    roll (e34, s35), the title menu and title GAME LOAD; states in work/states/ (`warp.py --all` regenerates;
    proof shots work/qa/warp/<scene>/final.png + work/qa/warp/sheet*.png). Every run passed (`warp.py --all`
    pieces run 2026-11-21: s00-s35, i08*, title*, e34).
  - `tools/debug/save.py` (layout + both checksums in `tools/debug/save_layout.md`, test tests/test_save.py):
    game-written intermission save work/saves/i08_saved.mcd edited to stage 20 loads via GAME LOAD with no error and
    NEXT TALE starts stage 20 (work/qa/load2). Fixture regen: `warp.py i08`, then emu.py --state-in
    work/states/i08.sstate --sav work/saves/blank.mcd --route-str "6 circle;400 -;6 circle;300 -;6 circle;300 -;6
    circle;300 -;6 circle;2000 -" and copy <out>/memcard1.mcd.
  - Game flow RE: `docs/re/debug.md` (exe chain, state block, stage table, event runner, stage-end calls).
- **Next (finish phase 2):** game over scene. Leads in `docs/re/debug.md` last bullet (FACE.DAT entry 106 "Game
  over" image caller; defeat event id via 0x80022eac; or zero player HP in battle). Add it to scenes.tsv, run
  `warp.py --all` once to confirm, then phase 3 (identity build: dumpsxiso/mkpsxiso rebuild byte-identical, and a
  rebuild that moves LBAs still warps to a battle).
- **Notes:** stage index != tale number (stage 8 shows "tale 7"); event stages 3/11/32 chain into the next stage.
  The portable card tools/pcsx/memcard1.mcd must stay blank (warp.py always passes a blank `--sav`).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
