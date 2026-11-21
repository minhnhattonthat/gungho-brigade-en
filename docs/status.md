# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 done). Last build: none yet.
- **Done:**
  - Step 0: dump pinned (`rom.sha1`), pre-commit hook (`tools/hooks`, runs `tools/check.py`; verified a failing test
    blocks a commit), guard hook verified (plugin blocks `sed -i`), PCSX-Redux + SCPH-5500 BIOS in `tools/`,
    mkpsxiso 2.30 + armips 0.11.0 in `tools/`, AGENTS.md filled, decisions D1-D8 recorded.
  - Emulator check on original disc: smoke ok, Start skips FMV to title (input works), Lua probe `L.log` lands in
    log.txt. Keyboard in the GUI not checked (headless worker).
  - Route to tale 1 battle from cold boot: `1500 -; start; 300 -; start; 600 -;` then circle every ~4 s (FMVs: start
    skips). States in work/qa/explore3 (s000480 = tale 1 card, s002880 = battle) - not committed, regenerate.
  - Recon notes: `docs/re/text.md` (encoding, files, SCENFILE overlay pointer format verified for tale 1),
    `docs/re/graphics.md` (TIM sweep run, 1 of 45 sheets reviewed). `tools/timscan.py` renders TIMs.
- **Next (finish phase 1):**
  1. Review the remaining 44 sweep sheets (`work/gfx/sweep`, regenerate with timscan.py; list in graphics.md) and
     list every Japanese element; second pass with `--min 8` for GAMEDATA icons.
  2. VRAM-dump the battle status window / command menu / name plate (tale 1) to tell font-drawn from TIM text.
  3. Find where unit/weapon/item names live (not SJIS, not glyph-index u8/u16; maybe GAMEDATA TIMs or another encoding).
  4. Confirm the glyph list (GUNHO.EXE +0x5db78) by hooking the draw call; locate the font bitmap.
  5. Check whether the EXE reads files by hard-coded LBA (decides whether files may grow) and the overlay buffer limit.
  Then phase 2 (debug tool: warp to any tale/battle).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
