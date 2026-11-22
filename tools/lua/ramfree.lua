-- RAM survey (docs/voice-subs-plan.md phase 3), needs emu.py --debugger (read watch):
-- FILL_AT frames after GUNHO.EXE appears in RAM (same test as tools/debug/warp.lua; filling at that frame hung the
-- boot: the loader still runs from low RAM), fill the candidate ranges with 0xA5, then
--   "READ <page>"  the first read of each 1 KB page of the filled ranges (the game uses it: not free),
--   "FREE <start> <end> f<frame>"  every 300 frames, the runs (>= 256 bytes) still holding the pattern.
-- Free = never read and never written after the fill.
--   emu.py ... --debugger --script tools/debug/warp.lua --var STAGE=8 --script tools/lua/ramfree.lua
-- RANGES: comma list of hex start-end (default: under GUNHO.EXE after the game-state block, and above TABLE.BIN up
-- to well under the stack).
local ffi = require("ffi")
local mem = PCSX.getMemPtr()
local function r32(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 + mem[a+2] * 65536 + mem[a+3] * 16777216 end
local ranges = {}
for s, e in string.gmatch(RANGES or "80010800-80020000,80176000-801f8000", "(%x+)-(%x+)") do
  ranges[#ranges + 1] = { tonumber(s, 16) % 0x200000, tonumber(e, 16) % 0x200000 }
end
local seen, filled = nil, false
local pages = {}
local function scan(n)
  for _, r in ipairs(ranges) do
    local a, run = r[1], nil
    while a < r[2] do
      local ok = mem[a] == 0xA5 and mem[a+1] == 0xA5 and mem[a+2] == 0xA5 and mem[a+3] == 0xA5
      if ok and not run then run = a end
      if (not ok or a + 4 >= r[2]) and run then
        local e = ok and a + 4 or a
        if e - run >= 256 then L.log(string.format("FREE %08X %08X f%d", 0x80000000 + run, 0x80000000 + e, n)) end
        run = nil
      end
      a = a + 4
    end
  end
end
L.on_frame(function(n)
  if not seen and r32(0x80086390) == 0x800844DC then seen = n end
  if seen and not filled and n >= seen + (FILL_AT or 120) then
    for _, r in ipairs(ranges) do
      ffi.fill(mem + r[1], r[2] - r[1], 0xA5)
      L.on_read(0x80000000 + r[1], 0x80000000 + r[2] - 1, function(addr)
        local p = math.floor((addr % 0x200000) / 1024)
        if not pages[p] then
          pages[p] = true
          L.log(string.format("READ %08X f%d pc%08X", 0x80000000 + p * 1024, L.frame, L.pc()))
        end
      end)
    end
    filled = n
    L.log(string.format("FILL f%d", n))
  elseif filled and (n - filled) % 300 == 299 then
    scan(n)
  end
end)
