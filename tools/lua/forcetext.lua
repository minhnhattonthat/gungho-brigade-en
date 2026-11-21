-- Force every string of a stage overlay through the real dialogue box (needs emu.py --debugger; load after
-- tools/debug/warp.lua, which mashes circle every MASH_EVERY frames). tools/tour.py drives it.
--   --var "TEXT_LIST='<abs path>'"   lines "id hexaddr": the strings to show, in order
-- 0x800506b0(faceL a0, a1, textL a2, faceR a3, [sp+0x10], textR [sp+0x14], [sp+0x18]) shows a dialogue box and
-- blocks in the menu runner until circle closes it, then returns through 0x8005075c (docs/re/debug.md §Dialogue).
-- The first call of the intro is hijacked: textL = the next listed string, no right speaker; at 0x8005075c the frame
-- is popped and the call re-entered with the next string until the list is done, then the intro goes on.
-- One shot per page, just before each mash press: t_<n>_<id>_p<page>.png. Log: "FORCE <n> <id> f<frame>".
local mem = PCSX.getMemPtr()
local function r32(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 + mem[a+2] * 65536 + mem[a+3] * 16777216 end
local function w32(a, v) a = a % 0x200000; for i = 0, 3 do mem[a+i] = math.floor(v / 256 ^ i) % 256 end end
local MASH = MASH_EVERY or 45
local list = {}
local f = io.open(TEXT_LIST or error("set --var TEXT_LIST='<file>'"), "r") or error("cannot open " .. TEXT_LIST)
for line in f:lines() do
  local id, a = line:match("^(%S+)%s+(%x+)")
  if id then list[#list + 1] = { id = id, addr = tonumber(a, 16) } end
end
f:close()
local idx, cur, page, saved, reentered = 0, nil, 0, nil, false

local function load_next(r)   -- r = GPR.n at the entry of 0x800506b0 (caller's frame)
  idx = idx + 1; cur = list[idx]; page = 0
  r.a0 = saved.a0; r.a1 = saved.a1; r.a2 = cur.addr; r.a3 = 0xFFFFFFFF
  w32(r.sp + 0x14, 0)
  L.log(string.format("FORCE %d %s f%d", idx, cur.id, L.frame))
end

L.on_exec(0x800506B0, function()
  if reentered then reentered = false; return end   -- args already set by the return hook
  if saved or #list == 0 then return end
  local r = PCSX.getRegisters().GPR.n
  saved = { a0 = r.a0, a1 = r.a1 }
  L.log(string.format("force: hijack f%d ra=%08X", L.frame, r.ra))
  load_next(r)
end)

L.on_exec(0x8005075C, function()
  if not cur then return end
  if idx >= #list then cur = nil; L.log(string.format("force: done f%d", L.frame)); return end
  local regs = PCSX.getRegisters()
  local r = regs.GPR.n
  local sp = r.sp
  r.ra = r32(sp + 0x1C); r.s0 = r32(sp + 0x18); r.sp = sp + 0x20
  load_next(r)
  reentered = true
  regs.pc = 0x800506B0
end)

-- warp.lua stops mashing at battle start, and some stages make their first dialogue call only then: mash here
-- while forcing (after warp.lua's callback, so its clearOverride doesn't undo it); end the run once done.
local done_at
L.on_frame(function(n)
  if not cur and idx > 0 and idx >= #list and not done_at then done_at = n end
  if done_at and n >= done_at + 60 then L.shot("final.png"); L.finish(0); return end
  if cur and n % MASH < 6 then PCSX.SIO0.slots[1].pads[1].setOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE) end
  if cur and n % MASH == MASH - 2 then
    L.shot(string.format("t_%03d_%s_p%d.png", idx, cur.id, page))
    page = page + 1
  end
end)
