"""Voice-clip (XA) subtitles for story scenes: docs/voice-subs-plan.md.

    python -X utf8 tools/voice.py clips                  -> the 200-entry clip table (clip, file, channel, seconds, ja)
    python -X utf8 tools/voice.py log [sNN..] [--jobs 3] -> work/qa/xa/<sNN>_<mode>/log.txt: warp runs with tools/lua/xalog.lua
    python -X utf8 tools/voice.py map                    -> work/voice/map.tsv: clip -> stages/events/callers it played in
    python -X utf8 tools/voice.py collect                -> script/voice/subs.tsv from the transcripts (once; then edited)
    python -X utf8 tools/voice.py batch [--size N]       -> work/tl/voiceN.tsv (untranslated lines, play order) + voice_ctx.tsv
    python -X utf8 tools/voice.py check voice1 ..        -> every id answered in work/tl/<b>.out.tsv, fits 2 x 50, has glyphs
    python -X utf8 tools/voice.py merge [voice1 ..]      -> English from work/tl/voice*.out.tsv into script/voice/subs.tsv
    python -X utf8 tools/voice.py build [--test]         -> cue blobs appended to work/build/files/SCENFILE.DAT + hooks
                                                            assembled into its GUNHO.EXE (insert.py runs this)

Clip table: GUNHO.EXE 0x80083e9c, 200 x {s16 file, s16 channel, u32 length}; file indexes the 17 name pointers at
0x80021324 (\\XA\\XA0nn.XA;1, 007-009 alias 006). Transcripts: work/xa/XAnnn_cc.ja.tsv (fmv.py transcribe).
"""
import argparse
import re
import struct
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXE = ROOT / 'work/disc/tree/GUNHO.EXE'
XA = ROOT / 'work/xa'
QA = ROOT / 'work/qa/xa'
WORK = ROOT / 'work/voice'
BLANK = ROOT / 'work/saves/blank.mcd'
SUBS = ROOT / 'script/voice/subs.tsv'
CLIPS, NCLIPS, NAMES = 0x80083e9c, 200, 0x80021324
RATE = 21900   # clip-table length units per second (= 365 per NTSC vsync; matches every wav's duration)


def off(addr):
    return addr - 0x80020000 + 0x800


def clips(exe=None):
    """[(clip, 'XAnnn', channel, length)] from the EXE's clip table."""
    d = (exe or EXE).read_bytes()
    names = []
    for i in range(17):
        p, = struct.unpack_from('<I', d, off(NAMES + 4 * i))
        names.append(re.search(rb'XA\d\d\d', d[off(p):off(p) + 16]).group().decode())
    out = []
    for c in range(NCLIPS):
        f, ch, ln = struct.unpack_from('<hhI', d, off(CLIPS + 8 * c))
        out.append((c, names[f] if 0 <= f < 17 else None, ch, ln))
    return out


def transcript(name, ch):
    p = XA / f'{name}_{ch:02d}.ja.tsv'
    if not p.exists():
        return []
    return [r.split('\t') for r in p.read_text(encoding='utf-8').splitlines() if r]


def cmd_clips(_):
    for c, name, ch, ln in clips():
        ja = ' / '.join(r[2] for r in transcript(name, ch)) if name else ''
        print(f'{c:3d} {name} ch{ch:02d} len={ln:<6d} {ja}')


def run(stage, mode, cue):
    out = QA / f's{stage:02d}_{mode}'
    cmd = [sys.executable, '-X', 'utf8', f'{SKILL}/scripts/emu.py', str(cue), '--out', str(out), '--sav', str(BLANK),
           '--debugger', '--frames', '40000', '--timeout', '2400', '--shot-every', '600',
           '--script', str(ROOT / 'tools/debug/warp.lua'), '--var', f'STAGE={stage}',
           '--script', str(ROOT / 'tools/lua/xalog.lua')]
    if mode == 'clear':
        cmd += ['--var', 'CLEAR=1']
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log = (out / 'log.txt').read_text(encoding='utf-8', errors='replace') if (out / 'log.txt').exists() else ''
    return stage, mode, p.returncode == 0 and 'arrived' in log, log.count('\nXA ')


def cmd_log(a):
    stages = [int(s.lstrip('s')) for s in a.stages] or list(range(36))
    jobs = [(s, m) for s in stages for m in ('battle', 'clear')]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda j: run(*j, a.cue), jobs))
    for s, m, ok, n in res:
        print(f"{'ok  ' if ok else 'FAIL'} s{s:02d} {m}: {n} clips")
    return 0 if all(r[2] for r in res) else 1


LINE = re.compile(r'^XA (\d+) f(\d+) stage=(-?\d+) ra=([0-9A-F]+) event=(-?\d+)')


def cmd_map(_):
    seen = defaultdict(list)
    for log in sorted(QA.glob('*/log.txt')):
        for row in log.read_text(encoding='utf-8', errors='replace').splitlines():
            m = LINE.match(row)
            if m:
                c, f, st, ra, ev = m.groups()
                seen[int(c)].append((log.parent.name, int(f), int(st), ra, int(ev)))
    WORK.mkdir(parents=True, exist_ok=True)
    out = ['clip\tfile\tseen\tja']
    used = 0
    for c, name, ch, ln in clips():
        hits = seen.get(c, [])
        used += bool(hits)
        where = ' '.join(sorted({f's{st:02d}e{ev}' for _, _, st, _, ev in hits}))
        ja = ' / '.join(r[2] for r in transcript(name, ch)) if name else ''
        out.append(f'{c}\t{name}_{ch:02d}\t{where}\t{ja}')
    (WORK / 'map.tsv').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{used}/{NCLIPS} clips seen -> {WORK / "map.tsv"}')


def cmd_collect(_):
    """work/xa/*.ja.tsv -> SUBS for every voice clip in the table (XA000 = BGM skipped); never overwrites it."""
    import fmv
    assert not SUBS.exists(), f'{SUBS} exists; edit it by hand'
    SUBS.parent.mkdir(exist_ok=True)
    out = ['id\tstart\tend\tja\ten']
    for c, name, ch, ln in clips():
        if name in (None, 'XA000'):
            continue
        k = 0
        for s, e, ja in transcript(name, ch):
            if ja in fmv.HALLUCINATIONS:
                continue
            s, e = fmv.voiced(XA / f'{name}_{ch:02d}.wav', float(s), min(float(e), ln / RATE))
            out.append(f'{name}_{ch:02d}_{k}\t{s:.2f}\t{e:.2f}\t{ja}\t')
            k += 1
    SUBS.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(len(out) - 1, 'lines ->', SUBS)


# ---- translation batches ----
TL = ROOT / 'work/tl'


def script_order(tree=None):
    """[(clip, stage or None)] in play order: each stage overlay's clip references in file order, then the clips no
    overlay names (battle barks etc.), by clip id."""
    import extract as x
    dat, offs, ends = x.scen_entries(tree or EXE.parent)
    seen, out = set(), []
    for e, xo in sorted(x.OVERLAYS.items(), key=lambda t: x.scen_overlay(dat, offs[t[0]], ends[t[0]], t[1])[1]):
        ovl, stage, _, text_end = x.scen_overlay(dat, offs[e], ends[e], xo)
        for i in range(text_end, len(ovl) - 1, 2):
            h, = struct.unpack_from('<H', ovl, i)
            if 0x4000 <= h < 0x4000 + NCLIPS and h & 0x3fff not in seen:
                seen.add(h & 0x3fff)
                out.append((h & 0x3fff, stage))
        for i in range(0, len(ovl) - 3, 4):
            w, = struct.unpack_from('<I', ovl, i)
            if w >> 16 in (0x2404, 0x3404, 0x2405, 0x3405) and 0x4000 <= w & 0xffff < 0x4000 + NCLIPS \
                    and w & 0x3fff not in seen:
                seen.add(w & 0x3fff)
                out.append((w & 0x3fff, stage))
    out += [(c, None) for c, name, _, _ in clips() if name not in (None, 'XA000') and c not in seen]
    return out


def cmd_batch(a):
    """work/tl/voiceN.tsv (id, speaker ?, form sub, limit 50x2, ja) in play order + voice_ctx.tsv (id, clip, stage)."""
    subs = [r.split('\t') for r in SUBS.read_text(encoding='utf-8').splitlines()[1:]]
    by = defaultdict(list)
    for r in subs:
        by[r[0].rsplit('_', 1)[0]].append(r)
    table = clips()
    rows, ctx, done = [], [], set()
    for c, stage in script_order():
        _, name, ch, _ = table[c]
        key = f'{name}_{ch:02d}'
        if key in done:
            continue
        done.add(key)
        for r in by.get(key, []):
            if a.all or not r[4].strip():
                rows.append(f'{r[0]}\t?\tsub\t{MAXCH}x2\t{r[3]}')
                ctx.append(f'{r[0]}\tclip {c}\t' + (f's{stage:02d}' if stage is not None else 'any stage (battle bark / '
                                                                                         'intermission)'))
    TL.mkdir(parents=True, exist_ok=True)
    n = -(-len(rows) // a.size)
    for k in range(n):
        (TL / f'voice{k + 1}.tsv').write_text(''.join(r + '\n' for r in rows[k * a.size:(k + 1) * a.size]),
                                              encoding='utf-8')
    (TL / 'voice_ctx.tsv').write_text(''.join(r + '\n' for r in ctx), encoding='utf-8')
    print(f'{len(rows)} lines -> {n} batches work/tl/voice1..{n}.tsv; context work/tl/voice_ctx.tsv')


def problems(en):
    """Why `en` can't be shown (empty list = fits)."""
    try:
        encode(en)
        wrap(en)
    except ValueError as e:
        return [str(e)]
    return []


def cmd_check(a):
    bad = 0
    for b in a.batches:
        ids = [r.split('\t')[0] for r in (TL / f'{b}.tsv').read_text(encoding='utf-8').splitlines() if r]
        out = TL / f'{b}.out.tsv'
        got = dict(r.split('\t', 1) for r in out.read_text(encoding='utf-8').splitlines() if r) if out.exists() else {}
        for i in ids:
            if i not in got:
                print(f'{b}: {i} missing')
                bad += 1
            else:
                for p in problems(got[i].strip()):
                    print(f'{b}: {i} {p}')
                    bad += 1
        for i in set(got) - set(ids):
            print(f'{b}: {i} not in the batch')
            bad += 1
    print('OK' if not bad else f'{bad} problems')
    return 1 if bad else 0


def cmd_merge(a):
    outs = [TL / f'{b}.out.tsv' for b in a.batches] or sorted(TL.glob('voice*.out.tsv'))
    en = dict(r.split('\t', 1) for p in outs for r in p.read_text(encoding='utf-8').splitlines() if r)
    rows = [r.split('\t') for r in SUBS.read_text(encoding='utf-8').splitlines()]
    for r in rows[1:]:
        r[4] = en.get(r[0], r[4]).strip()
    SUBS.write_text(''.join('\t'.join(r) + '\n' for r in rows), encoding='utf-8')
    print(sum(1 for r in rows[1:] if r[4]), 'of', len(rows) - 1, 'translated')


# ---- build: cue blob + hooks (tools/asm/voicesubs.asm) ----
ASM = ROOT / 'tools/asm/voicesubs.asm'
ARMIPS = ROOT / 'tools/armips/armips.exe'
MAGIC = b'VSUB'
ROOM = 0x2000            # DATA 0x8001e000..0x80020000
VSYNC = 60               # NTSC
MAXCH = 50               # 6-px small font, 300 px
LINE_Y = (201, 212)      # two lines; one line uses the lower
HOLD = 30                # vsyncs a cue stays after its speech (bridged up to the next cue)
HOOKS = [(0x800302fc, 4), (0x800316bc, 4), (0x80051e2c, 8), (0x8005aee0, 8), (0x8004f024, 0x8004f27c - 0x8004f024)]


def encode(text):
    import smallfont
    out = bytearray()
    for ch in text:
        if ch in smallfont.PUNCT:
            out.append(smallfont.PUNCT[ch])
        elif ch == ' ' or ch.isascii() and (ch.isalnum() or ch == ':'):
            out.append(ord(ch))
        else:
            raise ValueError(f'no small-font glyph for {ch!r} in {text!r}')
    return bytes(out)


def wrap(text, width=MAXCH):
    """Greedy word wrap; balanced into two lines when one doesn't fit."""
    if len(text) <= width:
        return [text]
    words = text.split()
    best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        if len(a) <= width and len(b) <= width and (best is None or max(map(len, best)) > max(len(a), len(b))):
            best = [a, b]
    if best is None:
        raise ValueError(f'over 2 lines of {width}: {text!r}')
    return best


def rows(test=False):
    """[(file_ch, start s, end s, en)] from SUBS; test=True fills empty en with the cue id."""
    out = []
    for line in SUBS.read_text(encoding='utf-8').splitlines()[1:]:
        i, s, e, ja, en = line.split('\t')
        en = en.strip() or (i.replace('_', ' ') if test else '')
        if en:
            out.append((i.rsplit('_', 1)[0], float(s), float(e), en))
    return out


def stage_clips(tree=None):
    """{stage 0-35: clip ids its overlay names} (halfwords 0x40NN past the text, `li a0/a1, 0x40NN`), and the set of
    voice clips no overlay names (battle barks, TABLE.BIN's): those go into every stage's blob."""
    import extract as x
    dat, offs, ends = x.scen_entries(tree or EXE.parent)
    per = {s: set() for s in range(36)}
    for e, xo in x.OVERLAYS.items():
        ovl, stage, _, text_end = x.scen_overlay(dat, offs[e], ends[e], xo)
        for i in range(0, len(ovl) - 3, 4):
            w, = struct.unpack_from('<I', ovl, i)
            if w >> 16 in (0x2404, 0x3404, 0x2405, 0x3405) and 0x4000 <= w & 0xffff < 0x4000 + NCLIPS:
                per[stage].add(w & 0x3fff)
        for i in range(text_end, len(ovl) - 1, 2):
            h, = struct.unpack_from('<H', ovl, i)
            if 0x4000 <= h < 0x4000 + NCLIPS:
                per[stage].add(h & 0x3fff)
    named = set().union(*per.values())
    common = {c for c, name, _, _ in clips(tree and tree / 'GUNHO.EXE') if name not in (None, 'XA000') and c not in named}
    return per, common


def blob(test=False, exe=None, only=None):
    """The cue blob DATA holds; only = clip ids to include (default all)."""
    by = defaultdict(list)
    for fc, s, e, en in rows(test):
        by[fc].append((s, e, en))
    table = [t for t in clips(exe) if only is None or t[0] in only]
    head = bytearray(MAGIC + struct.pack('<iI', -1, 0) + bytes(2 * NCLIPS))
    body = bytearray()
    lists = {}
    for c, name, ch, ln in table:
        cues = sorted(by.get(f'{name}_{ch:02d}', []))
        if not cues:
            continue
        clip_end = ln * VSYNC // RATE
        key = f'{name}_{ch:02d}'
        if key not in lists:   # clips sharing a channel share the list
            items = []
            for k, (s, e, en) in enumerate(cues):
                v0 = round(s * VSYNC)
                nxt = round(cues[k + 1][0] * VSYNC) if k + 1 < len(cues) else clip_end + HOLD
                v1 = min(max(round(e * VSYNC) + HOLD, v0 + VSYNC), nxt)
                lines = wrap(en)
                ys = LINE_Y[-len(lines):]
                text = bytearray()
                for t, y in zip(lines, ys):
                    w = len(t) * 6
                    text += bytes([(320 - w) // 4, y, (w + 1) // 2]) + encode(t) + b'\0'
                items.append((v0, v1, bytes(text + b'\xff')))
            lists[key] = items
    # layout: header, then per channel list (6 B per cue + end marker), then texts (2-aligned)
    pos = len(head)
    offs = {}
    for key, items in lists.items():
        offs[key] = pos
        pos += 6 * (len(items) + 1)
    texts = bytearray()
    for key, items in lists.items():
        for v0, v1, text in items:
            if (pos + len(texts)) & 1:
                texts += b'\0'
            o = pos + len(texts)
            texts += text
            body += struct.pack('<HHH', v0, v1, o)
        body += struct.pack('<HHH', 0xffff, 0xffff, 0)
    for c, name, ch, ln in table:
        key = f'{name}_{ch:02d}'
        struct.pack_into('<H', head, 0xc + 2 * c, offs.get(key, 0) if name not in (None, 'XA000') else 0)
    out = bytes(head + body + texts)
    assert len(out) < 0x10000
    return out


def scen_end(overlay, tree=None):
    """End of the last SCENFILE entry in the overlay copy (= where the cue blobs start, 0x800-aligned up): the last
    entry is not a text overlay, so it keeps its pristine size; its offset comes from the overlay's SCENFILE.LEN."""
    tree = tree or EXE.parent
    old = (tree / 'SCENFILE.LEN').read_bytes()
    ln = overlay / 'SCENFILE.LEN'
    new = ln.read_bytes() if ln.exists() else old
    last_old, last_new = struct.unpack_from('<I', old, len(old) - 4)[0], struct.unpack_from('<I', new, len(new) - 4)[0]
    return last_new + (tree / 'SCENFILE.DAT').stat().st_size - last_old


def apply(overlay, tree=None, test=False):
    """Append the cue blob to overlay SCENFILE.DAT and assemble the hooks into overlay GUNHO.EXE."""
    tree = tree or EXE.parent
    for n in ('SCENFILE.DAT', 'GUNHO.EXE'):
        if not (overlay / n).exists():
            (overlay / n).write_bytes((tree / n).read_bytes())
    per, common = stage_clips(tree)
    blobs, where, sizes = [], [], {}
    for s in range(36):
        b = blob(test, tree / 'GUNHO.EXE', per[s] | common)
        assert len(b) <= ROOM, f'stage {s}: cue blob {len(b)} B > {ROOM}'
        sizes[s] = len(b)
        if b not in blobs:
            blobs.append(b)
        where.append(sum(-(-len(x) // 0x800) for x in blobs[:blobs.index(b)]))
    # the last blob is padded to a full ROOM so every read stays inside the file
    tail = b''.join(x.ljust(-(-len(x) // 0x800) * 0x800, b'\0') for x in blobs[:-1]) + blobs[-1].ljust(ROOM, b'\0')
    scen = (overlay / 'SCENFILE.DAT').read_bytes()[:scen_end(overlay, tree)]
    off = -(-len(scen) // 0x800) * 0x800
    (overlay / 'SCENFILE.DAT').write_bytes(scen.ljust(off, b'\0') + tail)
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'dir.bin').write_bytes(struct.pack('<36H', *where))
    subprocess.run([str(ARMIPS), str(ASM), '-root', str(overlay), '-definelabel', 'VOFF', str(off),
                    '-strequ', 'DIRBIN', (WORK / 'dir.bin').as_posix()], check=True)
    return sizes


def ranges(name):
    """GUNHO.EXE bytes the hooks may change (diffcheck)."""
    return [(a - 0x8001f800, a - 0x8001f800 + n) for a, n in HOOKS] if name == 'GUNHO.EXE' else []


def cmd_build(a):
    overlay = Path(a.overlay)
    sizes = apply(overlay, test=a.test)
    print(f'cue blobs (largest {max(sizes.values())} of {ROOM} B, stage {max(sizes, key=sizes.get)}) -> '
          f'{overlay / "SCENFILE.DAT"}; hooks -> {overlay / "GUNHO.EXE"}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('clips')
    p = sub.add_parser('log')
    p.add_argument('stages', nargs='*')
    p.add_argument('--jobs', type=int, default=3)
    p.add_argument('--cue', default=str(ROOT / 'build/gungho_en.cue'))
    sub.add_parser('map')
    sub.add_parser('collect')
    p = sub.add_parser('build')
    p.add_argument('--overlay', default=str(ROOT / 'work/build/files'))
    p.add_argument('--test', action='store_true', help='cues without English show their id')
    p = sub.add_parser('batch')
    p.add_argument('--size', type=int, default=140)
    p.add_argument('--all', action='store_true', help='also lines that already have English')
    for n in ('check', 'merge'):
        sub.add_parser(n).add_argument('batches', nargs='*')
    a = ap.parse_args()
    return {'clips': cmd_clips, 'log': cmd_log, 'map': cmd_map, 'collect': cmd_collect, 'build': cmd_build,
            'batch': cmd_batch, 'check': cmd_check, 'merge': cmd_merge}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
