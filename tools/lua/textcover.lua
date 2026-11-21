-- Text coverage for PCSX-Redux (needs emu.py --debugger): log "TEXT <key>" for each string the game starts reading,
-- for $SKILL/scripts/textcover.py with build/strings.tsv (tools/insert.py writes it).
--   emu.py ... --debugger --script tools/lua/textcover.lua
-- Key = djb2-xor of the bytes from the read address to the NUL (insert.text_key), logged when the byte before is NUL;
-- after a 0x0A only the line up to the next 0x0A/NUL (staff roll rows are lines of one blob). Content keys follow
-- relocation and tell apart the 36 stage overlays that share one buffer. TEXT_SKIP_PC = comma list of hex PCs to
-- ignore (bulk copies). Each distinct (address, key) is logged once, with frame and PC.
local bit = require("bit")
local mem = PCSX.getMemPtr()
local function rb(a) return mem[a % 0x200000] end
local skip = {}
for pc in string.gmatch(TEXT_SKIP_PC or "", "%x+") do skip[tonumber(pc, 16)] = true end
local seen = {}
local function key(a, line)
  local h = 5381
  for i = 0, 2047 do
    local c = rb(a + i)
    if c == 0 or (line and c == 10) then break end
    h = bit.bxor(bit.lshift(h, 5) + h, c)
  end
  return bit.tohex(h)
end
local function hook(addr)
  local p = rb(addr - 1)
  if p ~= 0 and p ~= 10 then return end
  if rb(addr) == 0 then return end
  local pc = L.pc()
  if skip[pc] then return end
  local k = key(addr, p == 10)
  local id = addr .. ":" .. k
  if seen[id] then return end
  seen[id] = true
  L.log(string.format("TEXT %s %08X f%d pc%08X", k, addr, L.frame, pc))
end
-- RAM ranges holding text (docs/re/text.md): stage overlay buffer, TABLE.BIN / ENDING.BIN buffer, the EXE text
-- ranges (GUNHO.EXE and MENU.EXE both load at 0x80020000), GUNHO.EXE pilot records and half-width names / name pool.
for _, r in ipairs({{0x80159170, 0x80170ED0}, {0x80020000, 0x80021C00}, {0x8004BD00, 0x8004CA00},
                    {0x80096EFC, 0x8009858C}, {0x800A0800, 0x800A1A40}}) do
  L.on_read(r[1], r[2] - 1, hook)
end
