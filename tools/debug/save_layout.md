# Gungho Brigade save layout (memory card)

One 8 KB block per save, file name `BISLPS-01902-0000000` (slot digit varies), written by TABLE.BIN (battle and
intermission module, loaded at 0x8015eed0). Offsets below are into the save file (block):

| Offset | Size | Field | Proven by |
|---|---|---|---|
| 0x000 | 0x80 | PS1 header `SC`, 1 icon frame, SJIS title `Ｇｕｎｇｈｏ　Ｂｒｉｇａｄｅ　　第７話までクリア　　０時間　２分` | card dump |
| 0x080 | 0x80 | icon | |
| 0x100 | u32 | checksum A = byte sum of 0x000-0x0FF + byte sum of 0x108-0x10F | two game-written saves; check code TABLE.BIN 0x8016a740-0x8016a760 |
| 0x104 | u32 | checksum B = byte sum of 0x108-0x1FFF | two game-written saves |
| 0x108 | 0x3AC | game-state block, byte-identical to RAM 0x80010000.. (see below) | save vs RAM dump at the same moment (work/qa/ram5) |
| 0x4B4 | rest | more state, packed differently from RAM (not mapped yet) | |

Game-state block (RAM 0x80010000, pointer at 0x800A1A98; also the save at +0x108):

| +Off | Size | Field |
|---|---|---|
| +0x00 | s16 | stage index 0-35 (`tools/debug/scenes.tsv`); MENU.EXE NEW GAME writes -1, GUNHO's NEW GAME branch (0x8003158c) turns it into 0; the victory routine 0x80031cd8 increments it. In a save made at the intermission it is the next stage (NEXT TALE plays it). |
| +0x04 | u32 | play time in frames (save title's 時間/分 come from it) |
| +0x08 | s16 | cleared by NEW GAME |
| +0x0a | 0xc8 | story flags, cleared by NEW GAME |
| +0xd4 / +0xd8 | u32 / u16 | mid-battle resume data; +0xd8 bit 0 = resume a battle (0x800315e4) |
| +0xe0 | 40 x 0x76 | unit table (pointer 0x800A1A9C); +0x54 = 0xFF marks an empty slot; +0x50 = HP (GameShark 80010130) |

Editor: `tools/debug/save.py` (`--stage`, `--poke OFF:SIZE=VAL`, fixes both checksums). Tested: the intermission
save `work/saves/i08_saved.mcd` edited to stage 20 loads with GAME LOAD (no error) and NEXT TALE starts stage 20.
Not mapped yet: names (pilot names come from GUNHO.EXE 0x777ec, not the save), money, parts inventory.
