# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (nearly done; Step 0 done). Last build: none yet.
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
- **Next (finish phase 1):**
  1. Review SCENFILE sweep sheets 04-12 (`work/gfx/comp/c7.png`, `c8.png` = 2x2 downscaled composites; regenerate
     sheets with `tools/timscan.py work/gfx/sweep SCENFILE.DAT` from work/disc/tree) and GAMEDATA `work/gfx/gd2`
     sheets 01-03, 05-21 (`timscan.py work/gfx/gd2 GAMEDATA.DAT --min 8 --dedupe --zoom 2`); add any Japanese to
     graphics.md. Codex review is unavailable (usage limit until 2026-11-26).
  2. Check TABLE/MENU.DAT for its own copy of the command-label TIM (graphics.md note) and the between-tale menu
     screens once the debug tool can reach them.
  Then mark phase 1 done and start phase 2 (debug tool: warp to any tale/battle).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
