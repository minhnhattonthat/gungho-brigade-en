-- Probe (needs emu.py --debugger): log every GUNHO.EXE file read, i.e. calls to 0x80036994
-- (a0 = dest buffer, a1 = CdlFILE*, a2 = byte offset, a3 = size), plus the caller and $gp.
-- CdlFILE structs (filled at boot by 0x80030274..): 0x800EC490 SCENFILE, 0x800DD358 GAMEDATA,
-- 0x800A24A8 BTMOTION, 0x800A25A8 WPMOTION, 0x800B2F38 FACE.DAT.
local names = { [0x800EC490] = "SCENFILE", [0x800DD358] = "GAMEDATA", [0x800A24A8] = "BTMOTION",
                [0x800A25A8] = "WPMOTION", [0x800B2F38] = "FACE" }
L.on_exec(0x80036994, function()
  local r = PCSX.getRegisters().GPR.n
  local a1 = tonumber(r.a1)
  L.log(string.format("%d read %s buf=%08X off=%X size=%X ra=%08X gp=%08X", L.frame, names[a1] or string.format("%08X", a1),
        tonumber(r.a0), tonumber(r.a2), tonumber(r.a3), tonumber(r.ra), tonumber(r.gp)))
end)
