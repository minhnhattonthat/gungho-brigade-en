-- Voice-clip log for PCSX-Redux (needs emu.py --debugger): log "XA <clip> ..." each time GUNHO.EXE starts an XA
-- clip, i.e. calls XA_Play(clip) at 0x80051e2c (its only caller is the sound dispatcher 0x80052a58, id | 0x4000).
--   emu.py ... --debugger --script tools/debug/warp.lua --var STAGE=8 --script tools/lua/xalog.lua
-- Logged: frame, clip, stage (s16 at 0x80010000), the dispatcher's caller ($ra saved on dispatcher entry), event id
-- (gp+0x9c8). Used by tools/voice.py map (docs/voice-subs-plan.md phase 1).
local mem = PCSX.getMemPtr()
local function r16(a) a = a % 0x200000; return mem[a] + mem[a+1] * 256 end
local caller = 0
L.on_exec(0x80052a58, function()
  local r = PCSX.getRegisters().GPR.n
  caller = tonumber(r.ra) % 0x100000000
end)
L.on_exec(0x80051e2c, function()
  local r = PCSX.getRegisters().GPR.n
  L.log(string.format("XA %d f%d stage=%d ra=%08X event=%d", tonumber(r.a0) % 0x10000, L.frame, r16(0x80010000),
        caller, r16(0x800A1B18)))
end)
