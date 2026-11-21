-- Write values into RAM on every frame of the run (stress saves: play time, stage before GAME SAVE).
--   emu.py ... --script tools/lua/poke.lua --var "POKE='80010004:4=14997C4,80010000:2=22'"   (hex ADDR:SIZE=VAL)
-- Writes happen at frame start, so the game's own per-frame updates (the play-time counter) may add a little.
local mem = PCSX.getMemPtr()
local pokes = {}
for a, n, v in string.gmatch(POKE or "", "(%x+):(%d)=(%x+)") do
  pokes[#pokes + 1] = {tonumber(a, 16), tonumber(n), tonumber(v, 16)}
end
assert(#pokes > 0, "poke.lua: set POKE")
L.on_frame(function()
  for _, p in ipairs(pokes) do
    local a, n, v = p[1] % 0x200000, p[2], p[3]
    for i = 0, n - 1 do mem[a + i] = math.floor(v / 256 ^ i) % 256 end
  end
end)
