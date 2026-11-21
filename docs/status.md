# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (not started; phase 1 recon done 2026-11-21). Last build: none yet.
- **Done:**
  - Step 0: dump pinned, pre-commit hook, guard hook, PCSX-Redux + BIOS, mkpsxiso + armips, AGENTS.md, decisions D1-D8.
  - Route to tale 1 battle from cold boot: `1500 -; start; 300 -; start; 600 -;` then circle every ~4 s. States in
    work/qa/explore3 (s001440 = battle, command menu next; not committed, regenerate).
  - Text recon (`docs/re/text.md`): SJIS story/overlay format; **second encoding = half-width cp932** for
    unit/pilot/weapon/ability names + battle messages (GUNHO.EXE ~200 strings, TABLE.BIN a few), drawn with a small
    8x12 font that already has A-Z a-z 0-9; **kanji font verified** (glyph list GUNHO.EXE +0x5db78 binary-searched by
    TABLE.BIN code, 11x11 1bpp bitmap, copies in GAMEDATA/MENU.DAT/OVTABLE.DAT); battle help line turns single bytes
    into spaces (code patch needed, phase 5); TABLE.BIN = battle code module at 0x8015eed0; files opened by ISO name
    (`cdrom:%s;1`), so LBAs may move (prove in phase 3).
  - Graphics survey (`docs/re/graphics.md`): FACE.DAT reviewed fully (~23 prologue history stills with burned-in
    Japanese captions, offsets listed; tale cards, maps, logos English); battle command-menu labels = GAMEDATA entry
    265 +0x131c TIM (12 labels); MENU/OPENING/OVTABLE/TABLE.BIN TIMs English; SCENFILE sheets 00-03 textless.
  - Tools: `tools/timscan.py` (+ `--zoom`, `--dedupe`), `tools/psxvram.py` (render PCSX VRAM dump).
  - Graphics survey complete: all SCENFILE and GAMEDATA sheets reviewed, no new Japanese; redraw list at the top of
    `docs/re/graphics.md` (FACE captions, command labels, small-font kana, `体験版`). Command-label TIM has one copy
    (GAMEDATA 0x361b78); MENU.DAT +0x29000 is a copy of the small font.
- **Next (phase 2, debug tool):** `tools/debug/` warp to any tale's battle, the between-tale menu (GAME SAVE /
  TUNE UP / STATUS / NEXT TALE), the prologue history stills, game over, map clear and the credits (ENDING.BIN)
  from a cold boot; `tools/debug/scenes.tsv` + `warp.lua` (AGENTS.md warp command). Find the tale/stage variable
  (RAM search around SCENFILE entry selection; tale N card = FACE.DAT 0xf8b800+) and the memory-card save format
  for `save.py`. Then confirm the between-tale screens' runtime text (graphics.md last row).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
