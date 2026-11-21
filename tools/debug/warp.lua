-- Warp to a scene from a cold boot (emu.py --script tools/debug/warp.lua --var "SCENE='<name>'").
-- Scenes: tools/debug/scenes.tsv (name, stage, notes). How it works (docs/re/debug.md):
--   title -> NEW GAME; as soon as GUNHO.EXE is in RAM (stage table word at 0x80086390), write the stage index
--   (halfword at 0x80010000, the game-state block MENU.EXE and GUNHO.EXE share) before GUNHO's stage loader
--   (0x80031638) reads it. Then mash circle (Japanese confirm) so dialogue advances.
-- Opt-in globals: STAGE=<n> (skip the table), NOMASH=1 (no circle mash), GOD=1 (pin the two leads' HP),
-- CLEAR=1 (win the stage right after its intro), ENDING=1 (staff roll after the intro), TOUR=1 (don't stop at
-- arrival), SETTLE=<frames after arrival>, GAMEOVER=1 (defeat line + "Game over" instead of the intro; use with NOMASH=1
-- to stop on the line), EVENT=<id> (run stage event id instead of intro 9; RE aid, ids unmapped).
-- GOD is untested (addresses from a GameShark code for the roster copy; battle may use another copy).
-- Run with --sav work/saves/blank.mcd (tools/debug/warp.py does): an intermission mash can save to the card.
local ffi = require("ffi")
local mem = PCSX.getMemPtr()
local function r32(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 + mem[a+2] * 65536 + mem[a+3] * 16777216 end
local function w16(a, v) a = a % 0x200000; mem[a] = v % 256; mem[a+1] = math.floor(v / 256) % 256 end
local function r16(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 end
WARP = { r32 = r32, r16 = r16, w16 = w16 }

local root = OUT:match("^(.*)/work/") or error("OUT is not under <repo>/work/: " .. OUT)
local stage = STAGE
if not stage then
  local f = io.open(root .. "/tools/debug/scenes.tsv", "r") or error("cannot open scenes.tsv under " .. root)
  for line in f:lines() do
    local name, st = line:match("^([^\t#]+)\t(%-?%d+)")
    if name == SCENE then stage = tonumber(st) end
  end
  f:close()
  if not stage then error("unknown SCENE: " .. tostring(SCENE)) end
end

-- Cold boot: logo + opening run ~1500 frames (deterministic on this BIOS), start skips to the title, which
-- loads ("Now loading") and then opens its menu on NEW GAME (~2700). The circle mash below confirms it.
L.press("-", 1500); L.press("start", 6); L.press("-", 300)

local GUNHO_SIG = 0x800844DC          -- first word of the stage table in GUNHO.EXE (0x80086390)
local written, cleared, arrived = false, nil, nil
L.on_frame(function(n)
  if not written and r32(0x80086390) == GUNHO_SIG then
    -- GUNHO's NEW GAME branch (0x8003158c, stage == -1) clears the state block, sets stage = 0 and later runs the
    -- stage-start init and intro event 9. Writing the stage index directly takes the mid-battle "continue" branch
    -- instead (no intro, no card). So patch the branch, before it runs, to store our stage:
    --   800315D4 addiu $s6,$zero,-1   ->  addiu $s6,$zero,N   ($s6 is only tested for nonzero, then cleared)
    --   800315D8 sw $zero,4($v0)      ->  sh $s6,0($v0)        (+4 is already zeroed by MENU's NEW GAME)
    if r32(0x800315D4) ~= 0x2416FFFF or r32(0x800315D8) ~= 0xAC400004 then error("GUNHO.EXE code moved: re-find the NEW GAME branch") end
    if stage ~= 0 then
      w16(0x800315D4, stage); w16(0x800315D8, 0x0000); w16(0x800315DA, 0xA456)
      w16(0x80010004, 0); w16(0x80010006, 0)   -- what the replaced store did
    end
    -- CLEAR=1: win the stage right after its intro. 0x800318D8 `jal 0x8002c504` (read the victory flag) becomes
    -- `jal 0x80031cd8`, the victory routine stage scripts call (stage++, gp+0x9d0 = -1), so the game takes its
    -- own stage-clear path (to the MENU.EXE intermission, or straight into the next stage). Restored below once
    -- it has fired, so the next stage plays normally.
    -- EVENT=<id>: run stage event <id> instead of intro event 9 (0x800318C8 addiu $a0,$zero,9)
    -- GAMEOVER=1: run event 6 ("unit destroyed", args gp+0x9a8/0x9ac) instead, with 0x8005146c (the overlay's
    -- check "event 6 for unit a0/a1", used only by each stage's defeat handler) forced to return 1: the handler's
    -- first check shows the leader's face, FACE 106 "Game over", the defeat line, then 0x80031cfc (title).
    if GAMEOVER then
      if r32(0x8005146C) ~= 0x3C03800A then error("GUNHO.EXE code moved: re-find the destroyed-unit check") end
      w16(0x8005146C, 0x0008); w16(0x8005146E, 0x03E0); w16(0x80051470, 0x0001); w16(0x80051472, 0x2402)
      EVENT = 6
    end
    if EVENT then
      if r32(0x800318C8) ~= 0x24040009 then error("GUNHO.EXE code moved: re-find the intro event call") end
      w16(0x800318C8, EVENT)
    end
    if CLEAR or ENDING then
      if r32(0x800318D8) ~= 0x0C00B141 then error("GUNHO.EXE code moved: re-find the post-intro victory check") end
      -- ENDING=1: call 0x80031f84 instead (loads ENDING.BIN and runs the staff roll; stage 34's overlay calls it).
      local target = ENDING and 0x80031F84 or 0x80031CD8
      local jal = 0x0C000000 + math.floor((target % 0x10000000) / 4)
      w16(0x800318D8, jal % 0x10000); w16(0x800318DA, math.floor(jal / 0x10000))
    end
    -- Arrival marker: the victory-flag getter 0x8002C504 gets `sh $ra,0x9d2($gp)` in its delay slot (was nop;
    -- gp+0x9d2 = 0x800A1B22 is referenced nowhere in GUNHO). Its call right after intro event 9 leaves
    -- 0x18E0 (ra 0x800318E0) there: the intro is over and the battle starts.
    if r32(0x8002C50C) ~= 0 then error("GUNHO.EXE code moved: re-find the victory-flag getter") end
    w16(0x8002C50C, 0x09D2); w16(0x8002C50E, 0xA79F); w16(0x800A1B22, 0)
    written = true
    L.log(string.format("%d warp: stage %d patched", n, stage))
  end
  if written and CLEAR and not cleared and r16(0x80010000) == stage + 1 then
    cleared = n
    w16(0x800318D8, 0xB141); w16(0x800A1B22, 0)
    L.log(string.format("%d clear: stage now %d", n, stage + 1))
  end
  if written and GOD then w16(0x80010130, 3000); w16(0x800101A6, 2300) end
  -- Arrived: battle start (marker), or with CLEAR the stage clear itself; the intermission menu (GUNHO + TABLE.BIN,
  -- not MENU.EXE) is up and still ~1000 frames later. Stop mashing, let it settle SETTLE frames, then end the run
  -- with final.png (+ --state-out). TOUR=1 keeps running to --frames instead (intro/dialogue tours).
  if written and not arrived then
    if GAMEOVER and r16(0x800A1B18) == 6 then   -- gp+0x9c8: event 6 posted; the defeat line opens a few hundred frames later
      arrived = n
      L.log(string.format("%d arrived: event 6 (game over), stage %d", n, r16(0x80010000)))
    elseif CLEAR and cleared then
      arrived = n
      L.log(string.format("%d arrived: stage clear, stage %d", n, r16(0x80010000)))
    elseif not CLEAR and r16(0x800A1B22) == 0x18E0 then
      arrived = n
      L.log(string.format("%d arrived: battle, stage %d", n, r16(0x80010000)))
    end
  end
  if arrived and not TOUR and n == arrived + (SETTLE or (cleared and 1500 or GAMEOVER and 600 or 120)) then
    PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
    L.shot("final.png"); L.log("final frame " .. n)
    if STATE_OUT then L.save_state(STATE_OUT) end
    L.finish(0)
    return
  end
  -- before the write: circle confirms NEW GAME; after it: advances dialogue until arrival (NOMASH: never)
  local mash = L.route_done() and (not written or not NOMASH) and not cleared and not arrived
  if mash and n % (MASH_EVERY or 45) < 6 then
    PCSX.SIO0.slots[1].pads[1].setOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
  elseif L.route_done() then
    PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
  end
end)
