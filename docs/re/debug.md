# Game flow and the debug tool (phase 2)

Addresses are RAM (GUNHO.EXE loads at 0x80020000, file offset = addr - 0x80020000 + 0x800, `$gp` = 0x800A1150).
All **verified** by the warp runs in `tools/debug/` unless marked.

- **EXE chain:** SLPS_019.02 (logos, opening movie) -> MENU.EXE (title menu NEW GAME / CONTINUE / GAME LOAD) ->
  GUNHO.EXE (stages, intermission, saves) -> back to MENU.EXE for the title. MENU.EXE reads a 4-byte magic at
  0x80010000 on start: `BOOT` from the boot exe, `NUNO` from GUNHO (0x8003129c, game over/quit), then zeroes it.
- **Game-state block** 0x80010000 (pointer 0x800A1A98): stage index s16 at +0, layout in
  `tools/debug/save_layout.md`. MENU.EXE NEW GAME (0x8002bce4) sets stage = -1; GUNHO's start (0x80031568) takes
  the NEW GAME branch on -1 (clears the block, stage = 0, then stage init 0x80025da0 and intro event 9), else the
  "continue" branch (mid-battle resume: no intro, loads BGM id from 0x80011350+0x462).
- **Stage table** 0x80086390, 36 records x 76 bytes: +0x0C tale/map no., +0x0E/+0x10/+0x14/+0x16/+0x18 SCENFILE
  entries (map data), +0x1A SCENFILE text/script overlay (loaded at 0x80159170), +0x1C overlay event dispatcher
  (function pointer), +0x08 a name pointer (not the shown tale title: stage 8 shows "tale 7 The Guns of Marineris").
  Event stages 3, 11, 32 chain straight into the next stage. Stage 35 "SYSTEM TEMP" plays the staff roll.
- **Events:** 0x80022eac(id, a1, a2) stores id at gp+0x9c8 and runs the stage's dispatcher (record +0x1C) as an
  event thread. Intro = id 9 (0x800318c8). Other ids (defeat, turn events) not mapped; ids 1-4 on stage 8 all showed
  the same in-battle dialogue.
- **Stage end:** overlays call 0x80031cd8 (victory: stage++, gp+0x9d0 = -1; GUNHO then goes to the intermission
  menu, TABLE.BIN code, or straight into the next stage) or 0x80031cfc (gp+0x978 = -1, back to MENU.EXE title; used
  after defeat animations, e.g. SCENFILE entry 56 +0x2a30). 0x80031f84 loads ENDING.BIN and runs the staff roll
  (called by overlays 174, 175, 176).
- **Warp patches** (warp.lua, applied the frame GUNHO.EXE appears in RAM, before it runs):
  0x800315d4/d8 store stage N in the NEW GAME branch; 0x800318d8 `jal 0x8002c504` -> `jal 0x80031cd8` (CLEAR) or
  `jal 0x80031f84` (ENDING); arrival marker `sh $ra,0x9d2($gp)` in 0x8002c50c (0x800A1B22 = 0x18E0 once the
  post-intro check runs).
- **Not reached yet:** a game over (defeat) screen. FACE.DAT entries 106 "Game over" / 107 "Map clear!" are English
  images; their caller is unknown. Next step: find who loads FACE entry 106 (a FACE loader call with 0x6a), or
  the defeat event id, or zero the player units' HP in battle (unit table 0x800100E0, HP +0x50, GameShark
  80010130 / 800101A6; the battle may use its own copy).
