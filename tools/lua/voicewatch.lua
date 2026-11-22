-- Voice-subtitle state probe (tools/asm/voicesubs.asm): every EVERY frames (default 100) log the blob magic at
-- DATA 0x8001e000, the active clip, its start vsync, the XA-playing flag and the vsync counter.
--   emu.py ... --script tools/debug/warp.lua --var STAGE=8 --var TOUR=1 --script tools/lua/voicewatch.lua
local mem = PCSX.getMemPtr()
local function r32(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 + mem[a+2] * 65536 + mem[a+3] * 16777216 end
local last
L.on_frame(function(n)
  local s = string.format("magic=%08X clip=%d t0=%d playing=%08X vs=%d", r32(0x8001e000), r32(0x8001e004) > 0x7fffffff
    and -1 or r32(0x8001e004), r32(0x8001e008), r32(0x800a1818), r32(0x800a0678))
  if n % (EVERY or 100) == 0 then L.log(string.format("f%d %s", n, s)) end
end)
