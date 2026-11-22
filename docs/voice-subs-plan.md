# Plan: subtitles for in-game voice (XA) in story scenes

Status: implemented 2026-11-22 (D19); as built see docs/re/voice.md. Differences from this plan: clip -> stage map
from the overlays' static 0x40NN references (the warp log only reaches intros); data per stage (8 KB free RAM) read at
each stage load from blobs after SCENFILE.DAT; draw hook = the frame swap 0x8005aee0 with the hover box's small-font
routine (not the dialogue renderer); timing = vsyncs since the XA-playing flag went up. Phases 5-6 (full visual QA,
release) still open: docs/status.md.

## Why it is needed (verified 2026-11-22)
- Story scenes outside the FMVs play voice clips from `XA/XA0nn.XA`. Spot check of Whisper transcripts
  (work/xa/*.ja.tsv) against script/: most voiced lines have **no text box** (辻強盗, アレスティングケーブル, 袋の口は
  閉じた, 駆動系が不調, 避難民の収容: no match; 片目の大将 s15_0320 and ビッグＷ s31_06a8 do match, reworded). Full
  count: 203 of the 208 voice channels hold speech (324 Whisper lines); only ~12 clips are mostly found in the
  script's JP (5-char run match). So English players miss nearly every voiced story beat today.

## What is known (static RE, GUNHO.EXE, load 0x80020000, file off = addr - 0x8001f800)
- XA files: 14 on disc, each 16 interleaved channels (37.8 kHz mono, 4-bit), one clip per channel = 224 channels.
  XA000 = 16 BGM tracks (up to 187 s). XA001-016 = voice/radio clips, 3-14 s each.
- `0x80021324`: 17 pointers to `\XA\XA0nn.XA;1` names (007-009 alias 006). Init at `0x80051d70` resolves them with
  CdSearchFile into the LBA table `0x8014d810[17]`.
- **`XA_Play(clip)` at `0x80051e2c`**: clip 0..199 indexes `0x80083e9c`, 8 bytes each `{s16 file, s16 channel,
  u32 length}`; sets CdlSetfilter(file 1, channel), seeks, plays; end LBA kept at `gp+0xac0`.
- Its only caller is the sound dispatcher at `0x80052a58`: `id & 0x4000` -> `XA_Play(id & 0x3fff)`, else SPU SE.
  So **one hook point** sees every voice clip.
- Stage overlays (SCENFILE) pass 35 clip ids as `li a0, 0x40NN` immediates; the rest come from script data, so the
  clip -> scene map must be logged at runtime.

## Design
1. **Data** `script/voice/subs.tsv`: `clip, start, end, ja, en` (seconds from clip start; Whisper timing,
   `tools/fmv.py transcribe work/xa/*.wav` already produces it per channel). A builder maps (file, channel) ->
   clip id via the 0x80083e9c table and encodes `en` with the dialogue digraph codec (tools/digraph.py), so the
   existing English font draws it.
2. **Cue blob** (~200 clips x ~3 cues x ~60 B ≈ 35 KB + index): too big for the 4 KB EXE padding proven safe.
   Options, cheapest first: (a) free RAM found by a watch run (largest never-written region during scenes),
   loaded from a new disc file `VOICE.DAT` by the game's own CD read routine at boot; (b) per-stage slice
   appended to each SCENFILE overlay tail (growth by whole 0x800 sectors is verified; bound 0x5d60).
3. **Hook** (armips, GUNHO.EXE): at `XA_Play` entry save `clip` and the VSync counter (`VSync(-1)`) to two words.
   At the sound-stop / end path clear them.
4. **Draw**: hook the per-frame routine that adds the dialogue box to the ordering table; when a clip is active,
   pick the cue for `(vsync_now - vsync_start) / 60`, and draw it with the game's dialogue text routine at a
   fixed band (top of screen when a text box is open, else bottom). Find both routines with a PCSX-Redux
   breakpoint on the GPU packet writes of a known box (s08 warp).
5. **Timing**: VSync-based; if the game pauses XA (menu, skip), track the CD position instead (gp+0xabc..0xac0
   holds start/end LBA; current sector from CdlGetlocL). Decide after measuring.

## Phases
| # | Work | Check |
|---|---|---|
| 1 | Lua log of `XA_Play` a0 + stage id over a warp tour of every story scene (tools/debug/warp.py --all) -> clip -> scene map; list which clips have no text box | every voiced clip seen once; 200 ids accounted for (used / unused) |
| 2 | Transcripts cleaned + translated (translator agents, scene context from the map); timing from Whisper | reviewer pass; each cue fits 2 lines of the box width |
| 3 | RAM survey (free region) + cue blob format + loader | unit test: blob roundtrip; boot + warp still fine |
| 4 | asm hooks (XA_Play entry, frame draw) under unicorn exact-PC tests, then `--debugger` interpreter run | tests; no hang over the warp tour |
| 5 | Visual QA: screenshot at each cue time per scene (visual-qa sheets), overlap with text boxes | qa_gate on the new manifests |
| 6 | diffcheck ranges for the hook + blob, release notes | check.py, release.py gates |

## Risks / open questions
- Free RAM for ~35 KB may not exist during battle-map scenes; fallback = per-stage blobs in overlays.
- Voices overlapping an open text box: draw band choice must not cover the box (phase 5 decides).
- Battle barks (if any clip plays in battle) may need a smaller font path (TABLE.BIN draws battle text).
- Whisper errors in radio-filtered clips: translator flags `UNSURE`, the user may listen to those.
