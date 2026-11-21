# Translator brief - Gungho Brigade (PlayStation)

Squad-tactics game on a war-torn, terraformed Mars: civilians and soldiers caught between the Martian Army and the
Earth Forces; Bizley's crew of rough misfits (from Rug Battle sport to real war) is the Gungho Brigade. Tone: gritty
military drama with banter and dark humour. Work only on the batches named in your dispatch, in order, each to a
passing check before the next.

## Read first (in parts: Read with offset/limit, the context plugin stubs whole files over ~4 KB)
1. `docs/style-reference.md` - voices and approved example pairs.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (`glossary.md` for the rest).
3. `docs/synopsis.md` - plot so far, who is who.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese body`. form: dlg (story/tutorial/objective box), help (one-line skill
description), name (small-font unit/weapon/skill name), credit (staff roll line), full (menu/memory-card message).
speaker = the JP speaker of this box, or `(name)` = last named speaker (a continuation box often is the same person
or the other party: read the neighbours). `/` in the JP body = its line breaks; ignore them, translate the box as one
utterance. limit `42x2` = 2 lines of 42 chars left after the speaker line: the HARD limit of the box.

## Output: `work/tl/<batch>.out.tsv` (file-write tool, never a heredoc)
`id<TAB>English body`, every id once, same order. Body only: no speaker name, no line breaks (batches.py adds the
speaker line and wraps at 42); ` / ` forces a break where the JP lays out a list or label rows. Keep 「」 as "...";
leave narration/objectives without quotes. ASCII only; not in the font: `/ \ ` { } | ~`. Dry run one line:
`python -X utf8 tools/batches.py fit <id> "<English>"`.

## Validate
`python -X utf8 tools/batches.py check <batch>` until it prints OK; `merge <batch>` writes it into script/.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Wordplay keeps its punch.
- The box is small (about 80-120 chars): be terse and spoken, drop filler, never drop information. If it can't fit,
  keep the meaning and report `LONG: id`.
- Voices per docs/style-reference.md; a line any speaker could have said is a mistake.
- Honorifics kept (-san, -kun, -chan); military ranks in English (Major Neeson). Names exactly as the glossary.
- Placeholders `%d %s [XX]` copied exactly; no suffix glued to a variable.

## Consistency
Never edit `glossary.md` mid-batch from a parallel agent; report `NEW TERM: jp -> en` (the controller merges).

## Report
Files written and entry count; then `NEW TERM:`, `UNSURE: id - note`, `LONG: id - note` lines.
