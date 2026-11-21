# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (menus + stress saves done, menu gate passes; final dialogue re-tour,
  tour gate re-init and textcover left). Last build: build/gungho_en.bin 2026-11-22 sha1 8591fa79. States in
  work/states/ for s01 s02 s30 s34 title* i08* go08* are from 8591fa79/7de18f57 (text-only diffs since b72aa484);
  the rest from de1e747c (regen `warp.py --all --cue build/gungho_en.cue` if a scene matters).
- **Done:**
  - Phase 8, fourth session (2026-11-22): menu + stress QA on the battle/intermission/title screens (play.py sessions
    work/play/mf, m34, h1; JP refs work/play/jp1, work/qa/jp_cfg). Manifest work/qa/menus/manifest.tsv (11 sheets,
    `qa_gate init ... work/qa/menus --glob "*.png" --build`), verdicts work/qa/menus/verdicts/self_001.tsv, check exits 0
    for 8591fa79. Fixes: battle config window row 2 (短縮) is drawn over the open "Config" button (JP too) and the
    window uses the GUNHO font (no fullwidth J Q R V Y Z b f j q v x y): row 1 "Fast", row 2 blank (D14, batches
    BLANK_OK + GUNHO_FULL lint, insert writes a fullwidth space). Help line widened lone 0x20 to 12 px: GUNHO.EXE pair
    rows now `aligned` (insert.aligned, used by fitcheck), 2 help rows reworded to fit. Ability box 11 chars
    (Ambidexter), Eqip Part column 6 (Right/Left/Pistol/Locked; s02_0150 tutorial says "Left"), Unit-tab header stops
    at 0x20 -> small-font spaces written as 0xA0, cell blanked by smallfont.py (D15, tests/test_insert.py). Memory-card
    messages use the menu font everywhere (all letters present). Stress save work/saves/stress_late.mcd (stage 34,
    99h58m; made with tools/lua/poke.lua over the i08 save route): save grid, overwrite prompt, GAME LOAD list ok.
    Graphics survey re-confirmed: title, Game over, intermission art, command buttons all English.
  - Phase 8, third session (2026-11-22):
    - Verdicts round 2: all 41 sheets read (self pass), work/qa/tour/verdicts/chunk_304b3673b140_00N.tsv +
      round2_followup.tsv (s07_0004 seen as s07_sheet_2's repeated last tile). s35 sheets: forced box is garbage
      (stage 35 loads no window texture) and the s35 overlay strings are never drawn in play (the s35 warp plays the
      ENDING.BIN roll), so ok with that note. `qa_gate.py check work/qa/tour/manifest.tsv work/qa/tour/verdicts` exits
      0 via `waive` for build de1e747c (only ENDING.BIN/FACE.DAT differ from the toured 7e91f4bb).
    - **Staff roll bug fixed** (e34 vs original, VRAM dumps work/qa/roll/vram_en|jp): each roll line is drawn into a
      VRAM strip x 320..511; English lines over 16 cells (32 chars, aligned pairs) spilled past x 512 into the picture
      texture: a glyph strip over the "System Programming" still and old roll text instead of the last still. 13
      ending rows now split with `{n}` (batches: credit = 32 chars x 3 lines, `/` rejected); `extract.roll_lines`
      keeps the 301 lines by taking one blank from the next run of 2+ blanks after each added line, so every section
      and the time-based Sign/TOMY logos stay in sync with the JP (work/qa/roll/e34_end.png pairs EN|JP). Test in
      tests/test_extract.py. docs/windows.md roll row updated.
    - **Prologue captions (D5) done:** tools/gfx_captions.py (in insert.GFX + diffcheck ranges): 23 FACE.DAT stills,
      caption pixels restored from each still's caption-free grey twin (colour 0x55c000: mask from 0x549000, refilled
      from nearby clean pixels), English in fonts/DejaVuSans-Bold.ttf 11 px, white + dark outline/halo. All 23 seen
      in the s02 intro on the build (work/qa/captions/captions_sheet*.png, late_zoom.png, late.png ~f4400-16980).
      Glossary rows added (Mars Year / Mars Century, Union of Martian States, Mars Union, Southern Confederation,
      Junk Rush, Lost Battalion...); docs/fonts.md row.
  - Phase 8, second session (2026-11-22): read all 72 tour sheets of build 49b6d4e9 (self pass, no reviewer
    available), verdicts in work/qa/tour/verdicts/chunk_45585d3d0368_00N.tsv: 63 ok, 9 issue, all fixed in script:
    s02_0538 grammar; one-word/unindented last lines in goal rows s05_0078, s10 victory x15, s13_005c, s30_00a4,
    s31_01f0, s34_0024 (now 9-space indent like the JP); s07_0004 had been shot on the intro still (tours before the
    repeat-first-string change: only s02/s09/s31 had it; every other stage's tile 1 was checked by eye and is fine).
    Rebuilt (digraph pairs now 1103), full re-tour `tour.py --jobs 7` incl. s35 (all 36 ok, s35 90/90 forced).
    `qa_gate init --build build/gungho_en.bin` -> 75 sheets, 41 without a current verdict (mostly each stage's last
    page, which gained the repeated first-string tile, plus the fixed rows and 3 new s35 sheets).
    Coverage list now includes s35: work/qa/tour/scen_strings.tsv = build/strings.tsv rows s00-s35 (2228);
    textcover 2227/2228, only s35_08bc (credits row, FORCE logged at f20401 but no TEXT key) failing.
  - Phase 8, first session (2026-11-22):
    - `tools/tour.py [sNN..] --jobs 6`: per stage, cold boot + warp, the intro's first dialogue call
      (0x800506b0, blocks in the menu runner, returns via 0x8005075c) is re-entered once per pointer-table string
      of the built overlay (`tools/lua/forcetext.lua`), so every stage string shows in the real 42x3 box: one shot
      per page `work/qa/tour/sNN/t_<n>_<id>_p<k>.png`, sheets `work/qa/tour/sNN_sheet*.png` (box cropped, 40 per
      page, readable at 1x). ~5-10 min per stage with --debugger, `--jobs 7` ok on this machine. **Done on build
      49b6d4e9 for s00-s34**: every string forced, every string one page (no box needs a second page); the first
      string is shown again at the end of the list (a hijack inside a mash press closes it unshot).
      Coverage of the 2139 stage strings s00-s34: 2139/2139 (`textcover.py work/qa/tour
      work/qa/tour/scen_strings.tsv`; scen_strings = strings.tsv minus s35/EXE/ending rows).
    - Text coverage: `tools/insert.py` writes `build/strings.tsv` (id -> djb2 key of the string's bytes, follows
      relocation and the shared overlay buffer); `tools/lua/textcover.lua` logs `TEXT <key>` on string-start reads
      (tour.py loads it). Report: `python -X utf8 $SKILL/scripts/textcover.py work/qa/tour work/qa/tour/strings.tsv`.
      Seen: menumv/menu keys hit by bulk readers at PC 8002B984/8003458C (boot copies): don't trust those as shown;
      pass `--var "TEXT_SKIP_PC='8002B984,8003458C'"` in runs for menu text, or waive slps/menumv (boot error text).
    - Battle command buttons redrawn (GAMEDATA 0x361b38 TIM, `tools/gfx_labels.py`, applied by insert.py, ranges in
      diffcheck; D13): Shoot Melee Item Morph Special Equip End / Unit List Save Goals Config End Plot. s04_0160 now
      says "Goals". Not yet seen in game (warp s01, circle on own unit then circle on a square: command menu).
    - docs/visual-qa-brief.md copied with this game's non-bugs (forced-tour context).
  - Phase 7 review fixes (2026-11-22, seventh session; ../.harness/reviews/gungho-brigade-en-phase7.md): small font
    now 6 px per char (tools/smallfont.py: 3 advance immediates + ASCII glyphs from font5 in both font TIMs; RE in
    docs/re/text.md §Small font), GUNHO.EXE name pool repacked (extract.repack_pool, word-only refs asserted) so 20
    shortened names are full again; name width is a hard lint error per window (`NAME_BUDGET`, docs/windows.md
    re-measured at 6 px: hover 10, STATUS pilot 14 / budget 12, skill 13, weapon 12 guess); glossary lint NFKC-normalises
    half-width JP; `batches.py check -v` fixed; six hover-box names still short (D12, docs/polish.md).
    tests/test_diffcheck.py (in the pre-commit check): clean insert passes, flipped EXE / overlay-code byte and junk
    after ENDING.BIN fail, smallfont ranges, pool and overlay-text reference claims. diffcheck bounds ENDING growth to
    the relocated roll; the old roll is zeroed; font writes read the overlay copy (no clobber); docstrings fixed.
    Not done (review Minor 9, optional): write log.
  - Phase 7 (2026-11-22, sixth session): `fitcheck.py` exits 0, `build.py` gates on new `tools/diffcheck.py` (per-file
    romdiff: changed bytes only in text slots / pointer tables / font bitmaps / relocated tails; negative-tested),
    tests/test_fit.py gates commits on fit, tests for overlay growth and ENDING relocation. How it fits:
    `...` = one 5-px "…" glyph in all digraph text (~550 B saved); SCENFILE overlays may grow after their pointer table
    by whole 0x800 sectors only (other sizes hang the next load; docs/re/text.md), only s35 grows; light rewording in
    s06/s11/s14/s20/s21/s26/s27 (D11); ENDING.BIN roll appended at the file end + its addiu repointed; small-font names
    shortened to slot (D9, list in docs/polish.md), batches lint now rejects `.`/`-`/`&` in small-font names;
    memory-card messages terse (D10), 短縮 = "Cut"; `to_full` keeps non-ASCII (○). Staff-roll noise bug fixed: the roll
    can't draw a glyph on a half cell, ending text is encoded `aligned` (e34 shots clean). New helpers
    tools/stagerows.py (rows that grew most per stage) and tools/tlshow.py (JP + batch body by id).
  - Phase 6 review fixes (2026-11-22, phase 7 session; review ../.harness/reviews/gungho-brigade-en-phase6.md):
    compose() now writes `{n}` for every fullwidth break (5 memory-card rows printed a literal `/`; lint rejects `/`
    in full rows); s00_0078 "- Battle/Fast/Status display", glossary 戦闘シーン/短縮 split into two rows; briefs
    docs/reviewer-brief.md + story-reviewer-brief.md copied; `pairs.py` also writes work/qa/nonstory/ (non-story
    pairs), read in full: report work/qa/story/reports/nonstory.md (ending_106 "Modeling" fixed, 2 minors to polish).
    Still owed: an **independent** reader (codex exec, quota back 2026-11-26) over the 36 chapters + non-story pairs
    before release (phase 9); current verdicts are self-review.
  - Phase 6 finished (2026-11-22, fifth session): review pass s08-s35 (self pass, Codex out of quota), verdicts in
    work/qa/story/verdicts/ (all 36 current). ~45 fixes: meaning (s21_0100 luck ran out, s32_0490, s31_0880, s27_0d70
    "to the east", s14_0af4), wording, goal rows ("or enemy wiped out"), US spelling everywhere (armor, favor,
    defense, memorized, fertilized, traveled, Color in credits), `!?` -> `?!` in dialogue, "Dad" for John's おとうさん.
    New minors in docs/polish.md. Fix loop: fixes as `id<TAB>body` in a scratch TSV, `tl_patch.py bNNN F`,
    `batches.py check bNNN` (don't pipe it: exit code), `merge bNNN --overwrite`.
  - Phase 6, fourth session (2026-11-22): non-story batches b001 ending, b002 gunho, b003 menu, b004 menumv, b005
    pilots, b043 slps, b044 table translated + merged (self-reviewed while writing; terms in glossary.md). Save title
    table_11800 = "Gungho Brigade #00 clear 00h 00m" (digits at the JP offsets; tests/test_batches.py checks it).
    batches.py: full-form " / / " = empty line. Review pass started: `tools/pairs.py` writes work/qa/story/chapters/
    sNN.txt (+ pages/sNN_KK.txt under 3.6 KB for reading) and doubles as the phase 9 story pass; manifest
    work/qa/story/manifest.tsv, verdicts work/qa/story/verdicts/sNN.tsv (s00-s07 current). Fixes: s05_0b68,
    s05_13c0, s06_0004, s06_14b0, s08_009c. Minors in docs/polish.md.
  - Phase 6, third session (2026-11-22): s20-s35 translated + merged (b026-b042); glossary (new units, Zion Canyon,
    sender/receiver, Special condition, Objective) and docs/synopsis.md to s35; docs/polish.md started (minor
    questions). batches.py: new form `roll` = scen_s35 from 0x420 (stage 35's own staff roll, 48 wide, 6 lines
    assumed, explicit ` / ` breaks, no auto-wrap). Tip: write drafts to the scratchpad and `cp` into work/tl (Write on
    work/tl then tl_patch triggers big change notices); dry-run long rows with `batches.py fit`.
  - Phase 6, second session (2026-11-22): s06-s19 translated + merged (b012-b025); glossary (places, units, Union
    terms, 「射撃」 Shoot / 「格闘」 Melee commands) and docs/synopsis.md extended to s19. New `tools/tl_patch.py bNNN
    FIX.tsv` (replace rows of a .out.tsv; write fixes with the file tool). Fit tip: a 42x2 row with its speaker line
    holds ~80 chars of body. Stock defeat lines: "Damn... Did I blow it?!", "Mustang... I'm sorry!", "Whoa! I'm hit!",
    "They got me. Bizley, heeelp!". Polish candidates: s14 "Mars Year 168" vs s17 "166" (JP as is); ルブルー = "Le
    Bleu" (guess); s08_0d5c/0d88 and s16_0250 JP end in a stray "v" (dropped).
  - Phase 6 so far (2026-11-22): `tools/batches.py` (split/check/merge/fit; translators write the body only, it adds
    the glossary speaker line, wraps at 42, keeps the JP's leading/trailing breaks; lint = glyphs, %s/%d, glossary,
    honorifics after katakana names, 42x3 box; tests/test_batches.py gates merged English). 44 batches in work/tl
    (b001 ending, b002 gunho, b003 menu, b004 menumv, b005 pilots, b006-b042 stages s00-s35 in order, b043 slps,
    b044 table; work/ is gitignored: `split` regenerates only untranslated ids, so after a fresh clone run
    `split --size 3500` and the numbers differ). glossary.md seeded (characters, all 43 speakers, places, terms),
    docs/translator-brief.md, docs/synopsis.md (to s05), docs/style-reference.md. Translated + merged: s00-s05.
    Codex is out of quota until 2026-11-26 (no `codex exec` translators/reviewers); translation is done by the worker
    itself, in story order. Fixed: extract.write_tsv wrote CRLF on Windows (now LF).
  - Phase 5 finished (2026-11-22, third session): width gate complete (docs/windows.md). Battle system menu = circle
    with the cursor on empty ground (unit list / save / goal / config / GO); config rows measured (table_00430 6
    chars, table_00440 4); battle messages gunho_00824/00834/00840 are never shown (debug sprintf into dead stack
    buffers, docs/re/debug.md); glyph torture in s08 dialogue draws every 5-px glyph clean (work/qa/torture/glyphs.png).
    New RE aid `tools/lua/callers.lua` (log calls of listed functions with $ra/args).
  - Phase 5 width gate (2026-11-22, second session): `tools/ruler.py` (slot-max ruler text, marker elsewhere).
    Measured: battle hover box unit name 8, weapon list 9, TUNE UP unit name 7 (slot), battle status pilot 7 /
    skill 10, help line 50 (46 seen clean), staff roll 48. All in docs/windows.md. Battle play session
    work/play/bt (play.py, from work/states/s01.sstate of the ruler build): circle on own unit = move range, circle
    again on a square, circle = command menu (射撃 ... END); circle on a weapon showed no target (none in range?);
    END plots the unit; triangle jumps the cursor to the next unit; select/hover = portrait box; L2/R2 rotate;
    start, cross and circle on empty ground opened nothing.
  - Phase 5 so far (2026-11-22): **font = digraphs, no code change** (tools/digraph.py, fonts/font5.txt; details
    docs/re/text.md §Font). Dialogue/battle text = pairs of 5-px letters in kana/kanji slots, 0x20 = 6-px space.
    MENU.EXE/SLPS/MENUMV/TABLE.BIN text = fullwidth Latin (their font is keyed by the real SJIS code; pairs showed as
    kana there). Small-font rows = ASCII. `tools/insert.py [--marker] [--qa ID=TEXT]` writes work/build/files/
    (rerun before build.py). tests/test_insert.py. `warp.py --all --cue build/gungho_en.cue` on the marker build:
    46/46 arrive, every dialogue/objective/tutorial box, help line, credits and memory-card message seen shows its
    marker (work/qa/warp/sheet*.png). Budgets: docs/windows.md (dialogue/tutorial/objective 42 chars x 3 lines).
  - Phase 4 (2026-11-21): `tools/extract.py` -> 43 `script/*.tsv` (2713 rows: 36 stage overlays 2228, gunho 135,
    pilots 123, ending 149, table 33, menu/slps/menumv 15 each), codec `tools/sjis.py` (cp932 tbl), refs scanner
    `tools/mipsrefs.py`, `extract.write_back()` (in-place, NUL-padded; insert base for phase 5/7).
    `tests/test_extract.py`: roundtrip, write-back identity, overlay sanity, TSV sync, disc-wide coverage. Details and
    formats: `docs/re/text.md` §SCENFILE text overlays, §Extraction.
  - Step 0 + phase 1 (recon, graphics survey): see git history, `docs/re/`.
  - Phase 3 (2026-11-21): `build.py` (check_rom, dumpsxiso if work/disc missing, mkpsxiso on a copy of layout.xml
    with absolute paths; any file under the overlay `work/build/files/<disc path>` replaces the tree file, unknown
    overlay paths refused). `tests/test_build.py`: slow test rebuild == rom.sha1 (passes), fast overlay tests.
    LBA move proven: GUNHO.EXE +4 KB in the overlay still warps to s08 battle, i08 intermission, e34 staff roll
    (files found by name; `docs/re/text.md` §Free space).
  - Phase 2 (2026-11-21): `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` warp from a cold boot to all 36 stages
    (intro, tale card, battle start), the intermission menu (GAME SAVE / TUNE UP / STATUS / NEXT TALE), the staff
    roll (e34, s35), the title menu and title GAME LOAD, and game over (go08: stage 8 leader's defeat line;
    go08_over: FACE 106 "Game over" image); states in work/states/ (`warp.py --all` regenerates; proof shots
    work/qa/warp/<scene>/final.png + work/qa/warp/sheet*.png). `warp.py --all` passed 2026-11-21 (all 46 scenes).
  - `tools/debug/save.py` (layout + both checksums in `tools/debug/save_layout.md`, test tests/test_save.py):
    game-written intermission save work/saves/i08_saved.mcd edited to stage 20 loads via GAME LOAD with no error and
    NEXT TALE starts stage 20 (work/qa/load2). Fixture regen: `warp.py i08`, then emu.py --state-in
    work/states/i08.sstate --sav work/saves/blank.mcd --route-str "6 circle;400 -;6 circle;300 -;6 circle;300 -;6
    circle;300 -;6 circle;2000 -" and copy <out>/memcard1.mcd.
  - Game flow RE: `docs/re/debug.md` (exe chain, state block, stage table, event runner + args, stage-end calls,
    defeat handler).
- **Next (phase 8, QA):**
  1. Final dialogue re-tour on 8591fa79 (`tour.py --jobs 7`, started in the fourth session; log
     work/qa/tour_run.log), then `qa_gate.py init work/qa/tour/manifest.tsv work/qa/tour --glob "*sheet*.png" --build
     build/gungho_en.bin` (unchanged sheets keep verdicts; s00/s02/s05 rows changed: re-read those sheets), check 0.
  2. Textcover: regenerate work/qa/tour/scen_strings.tsv = build/strings.tsv rows s00-s35, run `textcover.py
     work/qa/tour work/qa/tour/scen_strings.tsv`, waive s35_* never drawn (s35_08bc) with a reason. Non-stage strings
     (gunho/pilots/table/menu/ending): run the menu routes with textcover.lua (`--debugger --script
     tools/lua/textcover.lua --var "TEXT_SKIP_PC='8002B984,8003458C'"`) or waive them citing work/qa/menus. Then
     phase 8 is done -> phase 9.
  Notes: battle Goals screen not reached from the system menu (flaky; same objective boxes as battle start, toured).
  Battle system menu: square, left*10, cross, circle (sometimes needs a retry of the step). s35 overlay strings never
  drawn in play (s35 warp shows the ENDING.BIN roll).
  Story verdicts are stale for s00/s05/s06/s11/s14/s20/s21/s26/s27 + nonstory (phase 7 rewording): rerun `pairs.py`,
  `qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"`, re-read changed pages, rewrite
  verdicts (phase 9 gate, with the independent reader). s08_078c/07e8/0870/08f0 not seen in the s08 intro tour.
  Digraph pairs used: 1105 of 1375 codes.
- **Notes:** stage index != tale number (stage 8 shows "tale 7"); event stages 3/11/32 chain into the next stage.
  The portable card tools/pcsx/memcard1.mcd must stay blank (warp.py always passes a blank `--sav`). Game over warp
  shows over the loading screen (battle view never drawn) and only the first leader's line; stage 0 has no defeat
  handler.
- **Open bugs:** none known (staff-roll noise fixed in phase 7: half-cell glyphs, see docs/re/text.md).
- **Waiting on the user:** nothing.
