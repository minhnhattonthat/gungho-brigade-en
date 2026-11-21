"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500] [--files scen_s00,scen_s01]   work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py fit ID "English body"  print the composed lines (dry run for one row)

Copied from the skill's assets/batches.py; ADAPTER fitted to this game (script/*.tsv, digraph dialogue box).
Batch TSV: id, speaker, form, limit, JP body. Output: work/tl/bNNN.out.tsv, id<TAB>English body, every id once, same
order. The translator writes only the body: the speaker line (glossary Characters table), line breaks (auto-wrap at
the box width, ` / ` forces one) and the JP's leading/trailing empty lines are added here, so script `en` holds the
final string tools/insert.py encodes.
"""
import re
import sys
import textwrap
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract as x  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"%[sd]|\[[0-9A-F]{2}\]")  # printf args and raw bytes; must survive translation
BREAK = re.compile(r"/|\{n\}")  # line breaks; placed by compose(), not the translator
VARIABLE = r"%[sd]"
# glossary ruling D1: kept after a (katakana) name; お兄さん, おじさん are words, not honorifics
HONORIFICS = {r"(?<=[ァ-ヿ])さん": "-san", r"(?<=[ァ-ヿ])ちゃん": "-chan", r"(?<=[ァ-ヿ])(くん|君)": "-kun"}
SPEAKER = re.compile(r"^([^「『（/{}：\s　][^「『（/{}：]{0,11}?)(/|\{n\}|)(?=[「『（])")
SMALL = re.compile(r"[\x20-\x7e｡-ﾟ]*")
FULLWIDTH_FILES = {"menu", "slps", "menumv", "table"}
# Measured budgets (docs/windows.md): chars per line, lines per box.
# roll = stage 35's own staff roll (scen_s35 from 0x420): shortcut: 48 wide like ENDING.BIN, line count unmeasured; check at the s35 warp (credits ~frame 7000).
BOX = {"dlg": (42, 3), "help": (50, 1), "credit": (48, 1), "roll": (48, 6), "full": (18, 5)}
FULL_LIMIT = {"table_00430": 6, "table_00440": 4, "table_11800": 32}  # 11800 = card save title (JP length)
NAME_BUDGET = {"pilot": 7, "weapon": 9, "unit": 8, "skill": 10}  # small font, display chars (soft: phase 7 engine work)


def form_of(fname, row):
    if SMALL.fullmatch(row["jp"]):
        return "name"
    if fname in FULLWIDTH_FILES:
        return "full"
    if fname == "scen_s35" and int(row["id"].split("_")[1], 16) >= 0x420:
        return "roll"
    return {"gunho": "help", "ending": "credit"}.get(fname, "dlg")


def docs():
    """(path, rows, entries); each entry adds speaker / prev (last speaker for context), form, body, pre, post."""
    for path in sorted(SCRIPT.glob("*.tsv")):
        rows = x.read_tsv(path)
        entries, last = [], ""
        for r in rows:
            e = dict(r, form=form_of(path.stem, r), speaker="", pre="", post="", sep="")
            jp = r["jp"]
            if e["form"] == "dlg":
                m = SPEAKER.match(jp)
                if m:
                    e["speaker"], e["sep"], jp = m[1], m[2], jp[m.end():]
                    last = m[1]
                lead = re.match(r"^((?:/|\{n\})*)", jp)[1]
                tail = re.search(r"((?:/|\{n\})*)$", jp)[1]
                e["pre"], e["post"] = lead, tail
                jp = jp[len(lead):len(jp) - len(tail)]
                e["prev"] = last
            e["body"] = jp
            e["_row"] = r
            entries.append(e)
        yield path, rows, entries


def needs_english(entry):
    return bool(entry["jp"].strip()) and not entry.get("en")


def group_of(entry):
    return entry["id"]


def entry_key(entry):
    return entry["id"]


def limit_label(entry):
    f = entry["form"]
    if f == "name":
        return f"{entry['max']}B"
    if f == "full":
        return f"{FULL_LIMIT.get(entry['id'], 18)}/line"
    w, n = BOX[f]
    if f == "dlg":
        n -= len(BREAK.findall(entry["pre"])) + (1 if entry["sep"] else 0)
        return f"{w}x{n}"
    return f"{w}"


def speakers():
    """JP speaker -> EN, from glossary rows tagged `speaker` in the notes column."""
    return {j: ens[0] for jps, ens, _, notes in glossary(True) if "speaker" in notes for j in jps}


def wrap(text, width):
    """Greedy word wrap; ` / ` forces a break. Leading spaces (indents) of each segment are kept."""
    out = []
    for seg in text.rstrip().split(" / "):
        out += textwrap.wrap(seg, width, break_long_words=False, break_on_hyphens=False) or [""]
    return out


def compose(entry, body, names=None):
    """Final string for script `en`: speaker + separator, wrapped body, the JP's leading/trailing breaks."""
    f = entry["form"]
    if f != "dlg":
        # a standalone `/` is a break; "a / / b" = an empty line between
        # the fullwidth renderer only breaks on {n}; `/` there would print a slash
        brk = "{n}" if f == "full" or "{n}" in entry["jp"] else "/"
        return re.sub(r" ?(?<!\S)/(?!\S) ?", brk, body.strip())
    names = speakers() if names is None else names
    head = ""
    if entry["speaker"]:
        sp = names.get(entry["speaker"], f"<{entry['speaker']}?>")
        head = sp + entry["sep"] if entry["sep"] else sp + ": "
    w = BOX["dlg"][0]
    if entry["speaker"] and not entry["sep"]:
        lines = wrap(head + body, w)
        head = ""
    else:
        lines = wrap(body, w)
    return entry["pre"] + head + "/".join(lines) + entry["post"]


def width_problems(entry, en):
    f = entry["form"]
    if f == "name":
        return []  # soft: see name_notes()
    if f == "full":
        lim = FULL_LIMIT.get(entry["id"], 18)
        lines = BREAK.split(en)
        slash = ["'/' is not a break in fullwidth text (use {n})"] if "/" in en else []
        return slash + [f"line over {lim}: {ln!r}" for ln in lines if len(ln) > lim]
    w, n = BOX[f]
    lines = BREAK.split(en)
    while lines and lines[-1] == "":
        lines.pop()
    out = [f"line over {w} chars ({len(TOKEN.sub('xx', ln))}): {ln!r}" for ln in lines if len(TOKEN.sub("xx", ln)) > w]
    if len(lines) > n:
        out.append(f"{len(lines)} lines, box holds {n}")
    if "<" in en and "?>" in en:
        out.append("speaker missing from glossary (tag its row `speaker`)")
    return out


ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#$%&'()*+,-.:;<>?@[]^_ ")


def encodable(entry, char):
    """Digraph font: fonts/font5.txt glyphs (no / \\ ` { } | ~); small font: ASCII; `/` and {n} are breaks."""
    if entry["form"] == "name":  # small 8x12 font: A-Z a-z 0-9 : @ (= mm) and half-width kana only (text.md)
        return char.isascii() and (char.isalnum() or char in " :@%") or char == "･"
    if entry["form"] == "full" and char == "○":  # real SJIS font (circle button), as in the JP
        return True
    return char in ALLOWED or char in "/{}n"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ" or "ｦ" <= char <= "ﾟ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    jp = BREAK.sub("", jp)
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary(with_notes=False):
    """[(JP forms, EN forms, avoid forms[, notes])] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [a.strip() for a in cells[4].split("/") if a.strip()] if len(cells) > 4 else []
            row = ([j.strip() for j in cells[0].split("/")], [e.strip() for e in cells[1].split("/")], avoid)
            rows.append(row + ((cells[3] if len(cells) > 3 else ""),) if with_notes else row)
    return rows


def problems(entry, en, terms):
    """Every rule, on one final (composed) string."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en).replace("{n}", "")
    if bad := sorted({c for c in plain if not encodable(entry, c)}):
        out.append(f"unencodable characters {bad}")
    if "\t" in en or re.search(r"\\u[0-9a-fA-F]{4}", en):
        out.append("escape sequence or tab in the English")
    if (want := Counter(TOKEN.findall(jp))) != (have := Counter(TOKEN.findall(en))):
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. %d")')
    en_terms = " ".join(BREAK.sub(" ", en).split()).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_form, en_form in HONORIFICS.items():
        if re.search(jp_form, BREAK.sub("", jp)) and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form}")
    return out + width_problems(entry, en)


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            if entry_key(e) in result:
                raise ValueError(f"duplicate batch key {entry_key(e)!r}")
            result[entry_key(e)] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size, files=None):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    index()
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    batches = []
    for path, _, entries in docs():
        if files and path.stem not in files:
            continue
        cur, chars = [], 0  # batches never span files: one stage per batch keeps the story in order
        for e in entries:
            if not needs_english(e) or entry_key(e) in taken:
                continue
            c = len(e["body"])
            if cur and (chars + c > size or len(cur) >= MAX_ENTRIES):
                batches.append(cur)
                cur, chars = [], 0
            cur.append(e)
            chars += c
        if cur:
            batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = []
        for e in batch:
            sp = e["speaker"] or (f"({e['prev']})" if e.get("prev") else "")
            rows.append(f"{e['id']}\t{sp}\t{e['form']}\t{limit_label(e)}\t{e['body']}")
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(e["jp"] for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8",
                                                      newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms, names):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    got = [r[0] for r in rows]
    if got != want:
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    final = {}
    for eid, body in rows:
        if eid in entries:
            if "{n}" in body:
                bad.append(f"{eid}: write breaks as ' / ', not {{n}}")
            final[eid] = compose(entries[eid], body, names)
            bad += [f"{eid}: {p}: {final[eid]!r}" for p in problems(entries[eid], final[eid], terms)]
    return bad, final


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if e["id"] in new and e.get("en") and e["en"] != new[e["id"]]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, rows, _ in docs():
        touched = False
        for r in rows:
            if r["id"] in new and r["en"] != new[r["id"]]:
                r["en"] = new[r["id"]]
                touched = True
                changed += 1
        if touched:
            x.write_tsv(path, rows)
    print(f"merged: {changed} entries changed")


def name_notes(entries):
    """Small-font names longer than their measured display budget: phase 7 engine work (D4: no abbreviations)."""
    out = []
    for e in entries.values():
        if e["form"] == "name" and e.get("en"):
            cat = ("pilot" if e["id"].startswith("pilot_") else "weapon" if "ﾏｶﾞｼﾞﾝ" in e["jp"] or "@" in e["jp"]
                   else "unit")
            if len(e["en"]) > NAME_BUDGET[cat] or len(e["en"]) > int(e["max"]):
                out.append(f"{e['id']}: {e['en']!r} {len(e['en'])} chars (budget ~{NAME_BUDGET[cat]}, slot {e['max']}B)")
    return out


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        size = int(args[args.index("--size") + 1]) if "--size" in args else 3500
        files = set(args[args.index("--files") + 1].split(",")) if "--files" in args else None
        return split(size, files)
    entries, terms, names = index(), glossary(), speakers()
    if cmd == "fit":
        print("\n".join(BREAK.split(compose(entries[args[0]], args[1], names))))
        print(problems(entries[args[0]], compose(entries[args[0]], args[1], names), terms) or "OK")
        return 0
    overwrite = "--overwrite" in args
    batch_names = [a for a in args if a != "--overwrite"]
    if cmd == "check" and not batch_names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        done = sum(1 for e in entries.values() if e.get("en"))
        print(f"{len(entries)} entries, {done} translated, {len(bad)} problems")
        print("\n".join(bad[:200]))
        if "-v" in args:
            print("\n".join(name_notes(entries)))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not batch_names:
        sys.exit(__doc__)
    failed = 0
    for batch in batch_names:
        bad, final = check_batch(batch, entries, terms, names)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(final, overwrite)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
