# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D7 came with the one-shot run brief (owner's standing answers for every project), 2026-11-21.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-21 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer. |
| D2 | 2026-11-21 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-21 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-21 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms; engine work before abbreviating (skill default, not contradicted). |
| D5 | 2026-11-21 | Graphics text left in Japanese | none (default), list | Translate all graphics text (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-21 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint without asking. |
| D7 | 2026-11-21 | Existing saves / memory cards | use user's, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-21 | Git identity | - | Already set by new-game.ps1; do not change it. |
| D9 | 2026-11-22 | Small-font names (unit/weapon/skill/part, GUNHO.EXE) longer than their slot | relocate + widen windows, shorten | Shortened to the slot (worker call under D4/D6, pre-approved run): the display windows themselves hold only 7-10 chars (docs/windows.md), so relocation alone gains 0-3 chars per name. No `.`/`-`/`&` (the small font lacks them). Each shortened name is listed in docs/polish.md. |
| D10 | 2026-11-22 | Memory-card / file-error messages (fullwidth, 2 bytes per letter, real SJIS font) | code patch for an ASCII path, terse English | Terse English ("Checking card... / Keep the card in."): no ASCII path in the renderer; "card" for Memory Card where needed. 短縮 config button = "Cut" (3-char slot). |
| D11 | 2026-11-22 | SCENFILE stages whose English outgrows the text region | trim English, grow the overlay | Both: "..." drawn as one "…" glyph everywhere (digraph), light rewording in s06/s11/s14/s20/s21/s26/s27; strings that still don't fit go after the overlay's pointer table, entry grown by whole 0x800 sectors (only s35 needs it). |
| D12 | 2026-11-22 | Small-font names longer than their window (phase 7 review: D9 left 66 over) | narrower pitch + repack (engine), shorten | Engine first (D4): small-font pitch 8 -> 6 px with ASCII glyphs redrawn from font5 (tools/smallfont.py), GUNHO.EXE name pool repacked so full names fit; hard lint per window (NAME_BUDGET). Six unit names still over the 10-char hover box run words together or drop letters (YankApache, CloneDevil, Chrome Dvl, C Dragoon2, SuperCobra, Cmd Ship), listed in docs/polish.md; glossary carries them as unit-name variants. Worker call, pre-approved run. |
| D13 | 2026-11-22 | Battle command buttons (TIM, 34/50-px faces, fixed sprite rects) | wider buttons (code), shorter labels | Labels redrawn in the font5 letters, centred: Shoot Melee Item **Morph** (変形; "Transform" is 45 px) Special Equip End / Unit List Save **Goals** (シナリオ目的; s04_0160 now names "Goals") Config End Plot. Synonyms, not abbreviations (D4). Worker call, pre-approved run. |
| D14 | 2026-11-22 | Battle config window: row 2 (短縮) is drawn over the open "Config" button (JP does the same), so "Cut" read as "Cunt g"; the window uses the GUNHO font (no fullwidth J Q R V Y Z b f j q v x y) | move/relocate row 2, other word on row 2, whole option on row 1 | Row 1 "Fast" (ON = shortened battle scenes), row 2 blank (fullwidth space; batches BLANK_OK); s00_0078 / s05_13c0 name it "Fast"; lint GUNHO_FULL rejects the missing glyphs. Worker call, pre-approved run. |
