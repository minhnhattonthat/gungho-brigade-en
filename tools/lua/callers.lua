-- Log every call of the functions in HOOKS (comma-separated hex addresses): frame, function, $ra, $a0-$a3.
--   emu.py ... --debugger --script tools/lua/callers.lua --var "HOOKS='80035e14,8002a1a0'"
-- RE aid: which code path runs when a button is pressed (docs/re/debug.md).
local function hex(v) return string.format("%08X", v % 0x100000000) end
for a in string.gmatch(HOOKS or error("set --var \"HOOKS='addr,addr'\""), "[%x]+") do
  local addr = tonumber(a, 16)
  L.on_exec(addr, function()
    local r = PCSX.getRegisters().GPR.n
    L.log(string.format("f%d %s ra=%s a0=%s a1=%s a2=%s a3=%s", L.frame, hex(addr), hex(r.ra), hex(r.a0),
                        hex(r.a1), hex(r.a2), hex(r.a3)))
  end)
end
