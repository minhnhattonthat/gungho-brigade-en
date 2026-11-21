# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | encoding, files with text, SCENFILE overlay pointer tables, glyph list | partly verified |
| graphics.md | TIM sweep, graphics-text survey | in progress |
| debug.md | exe chain, game-state block, stage table, events, stage end, warp patches | verified (warp runs) |
| ../../tools/debug/save_layout.md | memory-card save layout + checksums | verified (2 game saves, edited save loads) |
