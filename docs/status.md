# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: next (phase 7 done 2026-11-22). Last build: build/gungho_en.bin 2026-11-22 =
  **full English** (`insert.py` + `build.py`), sha1 3e2e9bc16c7bf24174ed0750226a90636741e833, smoke ok. States in
  work/states/ = English build (`warp.py --all` 46/46 ok; e34 and s14 regenerated on the final build, the rest on the
  build just before it, which differed only in ENDING.BIN).
- **Done:**
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
- **Next (phase 8, QA):** QA tour of changed scenes on the English build (warp states ready) -> contact sheets,
  `qa_gate.py init/todo`, visual-QA verdicts in a fresh read-only pass (no reviewer agents: do it yourself or `codex
  exec`, quota back 2026-11-26), `qa_gate.py check` exit 0; graphics-text rows English in zoomed cold-boot shots (chapter
  cards, game over, credits) per D5; `inkbox.py` on choice/centred boxes; stress saves (`save.py`: longest names,
  full lists, max numbers); `textcover.py` exit 0. Specific checks owed:
  - small-font names in battle hover box / weapon list / STATUS / TUNE UP (shortened, D9; docs/polish.md list); try
    pairs for table_00440 ("Fast"); memory-card messages (title GAME LOAD, intermission GAME SAVE: 18 chars/line).
  - s35's grown overlay: its own roll/sound-list strings (s35_0004.., s35_0420..) were never seen on screen (s35 warp
    shows the ENDING.BIN roll); textcover will tell if anything reads them.
  - the "…" glyph in dialogue is checked (s14 --qa shot); help line (gunho_* descriptions) not yet seen in English.
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
