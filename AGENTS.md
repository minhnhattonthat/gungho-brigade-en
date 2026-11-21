# Gungho Brigade (PlayStation) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`        -> build/gungho_en.bin + .cue (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; slow tests: `python -X utf8 -m pytest -m slow`)
- Hooks:    `git config core.hooksPath tools/hooks` (once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/gungho_en.cue --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene..> [--cue build/gungho_en.cue]` / `--all` (regen every state in work/states/) / `--list`. Scenes: `tools/debug/scenes.tsv`; options in `tools/debug/warp.lua`; notes `docs/re/debug.md`. Never ask the user to play to a scene.
- Saves:    `python -X utf8 tools/debug/save.py CARD.mcd --show | --out NEW.mcd --stage N --poke OFF:SIZE=VAL` (layout `tools/debug/save_layout.md`); boot with `emu.py --sav NEW.mcd`.
- Release:  `python -X utf8 tools/release.py` (xdelta vs the .bin + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Gungho Brigade (Japan).bin/.cue` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own PCSX-Redux in `tools/pcsx/` (nightly 32338.20261121.15, `fetch_emu.py pcsx`; gitignored), BIOS `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`). Savestates: `work/states/`.
- Disc tools (gitignored): `tools/mkpsxiso/mkpsxiso-2.30-win64/{dumpsxiso,mkpsxiso}.exe` (github.com/Lameguy64/mkpsxiso v2.30), `tools/armips/armips.exe` (Kingcom/armips v0.11.0). xdelta3 on PATH.
- Disc: pristine unpack `work/disc/tree` + `layout.xml` (never edit); patched files go in `work/build/files/<disc path>`, which `build.py` swaps in.
- Text: `script/` (TSV). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- PS1: close any emulator holding build/*.bin before building. Japanese games confirm with circle.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
