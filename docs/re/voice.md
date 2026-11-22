# Voice clips (XA) and the voice-subtitle hooks

GUNHO.EXE addresses (load 0x80020000, file offset = addr - 0x8001f800). **verified** = seen in the emulator
(work/qa/voice, work/qa/xa) or under unicorn (tests/test_voice.py).

## Clips
- 14 XA files x 16 channels. Clip table 0x80083e9c: 200 x {s16 file, s16 channel, u32 length}; file indexes the 17
  name pointers at 0x80021324 (`\XA\XA0nn.XA;1`, 007-009 alias 006). Length unit: 21900 per second (= 365 per NTSC
  vsync; every channel's wav duration matches). XA000 = 16 BGM clips; 184 voice clips. **verified**
- `XA_Play(clip)` 0x80051e2c, only caller the sound dispatcher 0x80052a58 (`id | 0x4000`). Sets gp+0x6c8
  (0x800a1818) = 0 at entry and -1 once CdlReadS is issued; start/end LBA at gp+0xabc / gp+0xac0. The poll
  0x80051c64 (every 8 vsyncs) pauses the CD and clears gp+0x6c8 at the end LBA. **verified** (voicewatch.lua)
- Audio starts well after XA_Play returns: XA_Play sets gp+0xac4 (0x800a1c14) = start LBA, the poll overwrites it
  with CdlGetlocP's position. The drive reads 150 sectors/s, 16-channel interleave (sector i = channel i % 16), so a
  clip's first sector is start + channel. Measured (s08 intro): drive moves 13-17 vsyncs after XA_Play, i.e. the
  clip is heard 0.25-0.4 s after it (more on hardware). swap_hook starts the subtitle clock only once the position
  is past start + channel, back-dated 3/8 vsync per sector already read. **verified** (unicorn; s08 run, clips 67,
  117: start moved +24 / +15 vsyncs vs the old XA_Play-time clock, user saw subtitles early before)
- Scripts don't call XA_Play directly: they queue the id; the dispatcher's caller in the s08 intro is the main loop
  (ra 0x800304fc). **verified**
- Which clips a stage plays: its SCENFILE overlay holds them as halfwords 0x40NN after the text (in script order) or
  `li a0/a1, 0x40NN` (146 clips). The other 38 (battle barks "Jackpot!", victory lines, TABLE.BIN's clip 74, ...)
  are named only by GUNHO.EXE / TABLE.BIN code tables. `voice.stage_clips()`. The warp tour log (xalog.lua, intros
  only) agrees with the overlay lists. **verified** (s01-s11 intros)

## Hooks (tools/asm/voicesubs.asm, built by tools/voice.py, run from insert.py)
- Frame flip = libgs GsSwapDispBuff 0x8005aee0 (17 GUNHO + 10 TABLE.BIN callers); GsDrawOt 0x8005b930 runs after it
  into the other buffer. At swap entry the finished frame is in the drawing buffer; immediate DrawPrim
  (0x80056b34: DrawSync, then send) draws on it, **but only after** 0x8005ad70(0, 0) (set the drawing offset to the
  current buffer + (x, y), what the window runner 0x80035e14 does before each window): without it nothing showed.
  **verified**
- Text: 0x80023034(a0 unused, a1 x, a2 y, a3 str) = the battle hover box's small-font string routine (8x11 cells,
  6-px pitch after smallfont.py, font TIM descriptor 0x800a1c58; 0x20 = advance only, 0x2d -> glyph 0xb0). The TIM is
  in VRAM in story scenes and 3D cutscenes. Punctuation: cells 0x80-0x8e (smallfont.PUNCT). **verified**
- Band: one DrawPrim packet {E1 0x400 (abr 0), TILE 0x62 black semi-transparent} = half brightness behind each line.
- Stage load: overlay read `jal 0x80036994` at 0x800316bc; boot: FACE.LEN read at 0x800302fc. Both hooked to read the
  stage's cue blob (stage = s16 at 0x80010000, outside 0..35 -> stage 0's) into DATA. READ(buf, CdlFILE, start, END)
  reads whole sectors and first waits for XA to stop. **verified** (unicorn; s08 run)
- DATA 0x8001e000-0x80020000: zero in all 44 GUNHO savestates; the sound buffer at 0x80018000 ends at 0x8001e000 in
  every one. Code: 0x8004f024-0x8004f27c, a debug routine (sprintf + BIOS file calls) that nothing references.
- Cue blobs sit after SCENFILE.DAT's last entry (sector-aligned, 'VSUB'); the game only reads entries through the
  LEN table, so the tail is never loaded by anything else.

## Not verified yet
- The dead routine never running and DATA never written by the game over a whole tour (watch in QA).
- Text boxes open while a voice plays: the band sits at y 201-223; boxes may overlap.
