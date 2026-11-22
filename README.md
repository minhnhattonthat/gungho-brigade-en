# Gungho Brigade English translation

Unofficial English fan translation of **Gungho Brigade** (ガンホー・ブリゲード; PlayStation, Tomy, 2000, SLPS-01902): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
or memory card helps most.

## Translation status

| Part | Status |
|---|---|
| Story dialogue, mission briefings, victory/defeat conditions, tutorials | Translated |
| Menus, unit/weapon/ability names, help lines, memory-card messages | Translated (some names shortened to fit, below) |
| Title screen, game over, battle command buttons, prologue captions | Translated (redrawn) |
| Staff roll | Translated |
| Video cutscenes (FMV) | Japanese audio, English subtitles (burned into the video) |
| Voiced lines in story scenes (XA audio) | Japanese audio, English subtitles (drawn in-game) |

Known issues:
- The battle hover box holds 10 characters, so a few unit names run words together or drop letters (YankApache,
  CloneDevil, Chrome Dvl, C Dragoon2, SuperCobra, Cmd Ship); the Eqip tab Item column shows 8 characters, as in the
  Japanese (the row below the list shows the full name).
- Readings of some staff names in the credits are best guesses.
- Start a new game: memory-card saves from the Japanese game are untested.
- Subtitles were transcribed and timed from the audio by machine, then translated; a few lines may be misheard or
  slightly off in timing.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched image

Needs Python 3.12+, [mkpsxiso](https://github.com/Lameguy64/mkpsxiso) 2.30 and [armips](https://github.com/Kingcom/armips)
0.11.0 in `tools/` (see AGENTS.md), xdelta3, and your own dump of the Japanese disc
([Redump](http://redump.org/): "Gungho Brigade (Japan)", one track).

```sh
git clone https://github.com/minhnhattonthat/gungho-brigade-en
cd gungho-brigade-en
# copy your dump to: rom/Gungho Brigade (Japan).bin + .cue
#   (.bin: 706,362,048 bytes, CRC32 F974BD94, MD5 32db47ab49de10a964361a862a89789c,
#    SHA-1 695ccbdad4a0f20ca59cd0e662bb883073f45b7c; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/fmv.py extract && python -X utf8 tools/fmv.py burn && python -X utf8 tools/fmv.py insert
                                                       # FMV subtitles (needs ffmpeg, Java 8 + jPSXdec 2.1)
python -X utf8 tools/insert.py                         # English text, fonts, graphics -> work/build/files/
python -X utf8 build.py                                # -> build/gungho_en.bin + .cue
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Tomy's and is included only so
the translation can be checked against it. Gungho Brigade is (c) Tomy; this project is not affiliated with them.
Do not share patched images.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
