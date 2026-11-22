"""FMV subtitle pipeline (MOVIE/*.STR, MOVIE2/*.STR: 320x240 15 fps MDEC + mono XA audio, 2336-byte sectors).

    python -X utf8 tools/fmv.py extract [NAME..]     -> work/fmv/<NAME>.str (2352-byte sectors) + .wav
    python -X utf8 tools/fmv.py transcribe [WAV..]   -> <WAV>.ja.tsv (start, end, Japanese) via faster-whisper
    python -X utf8 tools/fmv.py collect              -> script/fmv/subs.tsv from the transcripts (once; then edited)
    python -X utf8 tools/fmv.py retime [ID..]        -> word-level times for over-long cues (or the ids given)
    python -X utf8 tools/fmv.py merge [OUT.tsv..]    -> English from work/tl/fmv*.out.tsv into script/fmv/subs.tsv
    python -X utf8 tools/fmv.py burn [NAME..]     -> work/fmv/<NAME>/sub/NNNN.png + replace.xml (English drawn on)
    python -X utf8 tools/fmv.py insert [NAME..]      -> work/fmv/out/<disc path> (jPSXdec -replaceframes; insert.py
                                                        copies these into the overlay, diffcheck runs check())

Subtitle lines: script/fmv/subs.tsv (id = <movie>_NN, start, end in seconds, ja = Whisper transcript, en); in a
subfolder because the script/*.tsv globs expect extract.py's columns.
"""
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / 'work/disc/tree'
OUT = ROOT / 'work/fmv'
SUBS = ROOT / 'script/fmv/subs.tsv'
SYNC = b'\x00' + b'\xff' * 10 + b'\x00'


def movies(names):
    found = {p.stem: p for d in ('MOVIE', 'MOVIE2') for p in sorted((TREE / d).glob('*.STR'))}
    return [(n, found[n]) for n in (names or found)]


def to2352(src, dst):
    """ffmpeg's psxstr demuxer wants raw 2352-byte sectors; dumpsxiso gives 2336 (no sync/header)."""
    d = src.read_bytes()
    assert len(d) % 2336 == 0, (src, len(d))
    with open(dst, 'wb') as f:
        for i in range(0, len(d), 2336):
            f.write(SYNC + b'\x00\x02\x00\x02' + d[i:i + 2336])


def extract(names):
    OUT.mkdir(parents=True, exist_ok=True)
    for n, p in movies(names):
        s = OUT / f'{n}.str'
        if not s.exists():
            to2352(p, s)
        w = OUT / f'{n}.wav'
        if not w.exists():
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'psxstr', '-i', s, '-vn', '-ar', '16000', w], check=True)
        print(n, 'ok')


def transcribe(wavs):
    """Any 16 kHz mono wavs (default: every FMV); writes <wav stem>.ja.tsv beside each, skipping done ones."""
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    # no CUDA runtime (cublas64_12) on this machine; default threads leave most of the 16 cores idle
    model = WhisperModel('large-v3', device='cpu', compute_type='int8', cpu_threads=8)
    for wav in map(Path, wavs or sorted(OUT.glob('*.wav'))):
        tsv = wav.with_suffix('.ja.tsv')
        if tsv.exists():
            continue
        with wave.open(str(wav)) as w:  # ndarray input: installed PyAV is too new for faster-whisper's decoder
            pcm = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        # VAD off: with it on, lines went missing (skill platform-ps1 note)
        segs, _ = model.transcribe(pcm, language='ja', vad_filter=False, condition_on_previous_text=False)
        rows = [f'{s.start:.2f}\t{s.end:.2f}\t{s.text.strip()}' for s in segs if s.text.strip()]
        tsv.write_text(''.join(r + '\n' for r in rows), encoding='utf-8')
        print(wav.stem, len(rows), 'lines')


HALLUCINATIONS = ('ご視聴ありがとうございました', 'ありがとうございました。', '次回予告')  # Whisper on silence/music


def voiced(wav, s, e, win=0.05):
    """Tighten [s, e] to the span whose 50 ms RMS is above a fifth of the segment's loudest window (VAD-off
    segments run over silence)."""
    import wave
    import numpy as np
    with wave.open(str(wav)) as w:
        rate = w.getframerate()
        pcm = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    seg = pcm[int(s * rate):int(e * rate)]
    n = int(win * rate)
    rms = np.array([np.sqrt(np.mean(seg[i:i + n] ** 2)) for i in range(0, max(len(seg) - n, 1), n)])
    on = np.nonzero(rms > rms.max() / 5)[0]
    if not len(on):
        return s, e
    return s + on[0] * win, s + (on[-1] + 1) * win


def collect(_):
    """work/fmv/*.ja.tsv -> SUBS (en empty; times tightened by voiced()); never overwrites it."""
    dst = SUBS
    assert not dst.exists(), f'{dst} exists; edit it by hand'
    dst.parent.mkdir(exist_ok=True)
    out = ['id\tstart\tend\tja\ten']
    for n, _ in movies([]):
        k = 0
        for row in (OUT / f'{n}.ja.tsv').read_text(encoding='utf-8').splitlines():
            s, e, ja = row.split('\t')
            if ja in HALLUCINATIONS:
                continue
            s, e = voiced(OUT / f'{n}.wav', float(s), float(e))
            out.append(f'{n}_{k:02d}\t{s:.2f}\t{e:.2f}\t{ja}\t')
            k += 1
    dst.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(len(out) - 1, 'lines')


def suspicious(s, e, ja):
    return e - s > len(ja) * 0.25 + 2.5  # longer than the words need: the segment includes music/silence


def retime(ids):
    """Word-level Whisper over each suspicious cue's span (or the ids given): start/end = first/last word. Rewrites SUBS
    times only."""
    import wave
    import numpy as np
    from faster_whisper import WhisperModel
    model = WhisperModel('large-v3', device='cpu', compute_type='int8', cpu_threads=8)
    rows = [r.split('\t') for r in SUBS.read_text(encoding='utf-8').splitlines()]
    for r in rows[1:]:
        i, s, e, ja = r[0], float(r[1]), float(r[2]), r[3]
        if not (i in ids if ids else suspicious(s, e, ja)):
            continue
        with wave.open(str(OUT / f'{i.rsplit("_", 1)[0]}.wav')) as w:
            rate = w.getframerate()
            w.setpos(int(s * rate))
            pcm = np.frombuffer(w.readframes(int((e - s) * rate)), np.int16).astype(np.float32) / 32768
        segs, _ = model.transcribe(pcm, language='ja', vad_filter=False, word_timestamps=True,
                                   condition_on_previous_text=False)
        words = [wd for sg in segs for wd in sg.words or []]
        if words:
            r[1], r[2] = f'{s + words[0].start:.2f}', f'{s + words[-1].end:.2f}'
        print(i, f'{s:.2f}-{e:.2f} ->', r[1], r[2], ja)
    SUBS.write_text(''.join('\t'.join(r) + '\n' for r in rows), encoding='utf-8')


FPS = 15
FONT = ROOT / 'fonts/DejaVuSans-Bold.ttf'
SIZE, STROKE, MARGIN, WIDTH = 13, 2, 8, 300  # px on the 320x240 frame


MIN_SHOW, HOLD = 1.5, 0.4  # s: shortest cue on screen; linger after the voice stops (never into the next cue)


def lines():
    """SUBS rows with English: (movie, first frame, last frame (1-based, as in the STR headers), en)."""
    rows = [r.split('\t') for r in SUBS.read_text(encoding='utf-8').splitlines()[1:] if r]
    rows = [(i.rsplit('_', 1)[0], float(s), float(e), en) for i, s, e, ja, en, *_ in rows if en.strip()]
    out = []
    for k, (m, s, e, en) in enumerate(rows):
        nxt = rows[k + 1][1] if k + 1 < len(rows) and rows[k + 1][0] == m else 1e9
        e = min(max(e + HOLD, s + MIN_SHOW), nxt - 1 / FPS)
        out.append((m, int(s * FPS) + 1, int(e * FPS) + 1, en))
    return out


def merge(outs):
    """work/tl/fmv*.out.tsv (id, en) -> the en column of SUBS."""
    en = dict(r.split('\t', 1) for p in (outs or sorted((ROOT / 'work/tl').glob('fmv*.out.tsv')))
              for r in Path(p).read_text(encoding='utf-8').splitlines() if r)
    rows = [r.split('\t') for r in SUBS.read_text(encoding='utf-8').splitlines()]
    for r in rows[1:]:
        r[4] = en.get(r[0], r[4]).strip()
    SUBS.write_text(''.join('\t'.join(r) + '\n' for r in rows), encoding='utf-8')
    print(sum(1 for r in rows[1:] if r[4]), 'of', len(rows) - 1, 'translated')


def wrap(draw, font, text):
    out, cur = [], ''
    for w in text.split():
        t = f'{cur} {w}'.strip()
        if cur and draw.textlength(t, font=font) > WIDTH:
            out.append(cur)
            t = w
        cur = t
    return out + [cur]


def burn(names):
    """Draw each English line on its frames: work/fmv/<NAME>/sub/NNNN.png (+ replace.xml for jPSXdec)."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(FONT), SIZE)
    todo = {}
    for m, a, b, en in lines():
        for f in range(a, b + 1):
            todo.setdefault(m, {})[f] = en
    for n in names or sorted(todo):
        d = OUT / n
        frames, sub = d / 'frames', d / 'sub'
        if not frames.exists():
            frames.mkdir(parents=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'psxstr', '-i', OUT / f'{n}.str', '-an',
                            frames / '%04d.png'], check=True)
        count = len(list(frames.glob('*.png')))
        assert min(todo[n]) <= count, (n, min(todo[n]), count)
        todo[n] = {f: en for f, en in todo[n].items() if f <= count}  # a cue's hold may run past the last frame
        if sub.exists():
            shutil.rmtree(sub)  # no stale frames from an earlier timing
        sub.mkdir()
        for f, en in sorted(todo[n].items()):
            im = Image.open(frames / f'{f:04d}.png').convert('RGB')
            dr = ImageDraw.Draw(im)
            rows = wrap(dr, font, en)
            assert len(rows) <= 2, (n, f, en)
            y = im.height - MARGIN - len(rows) * (SIZE + 3)
            for r in rows:
                dr.text(((im.width - dr.textlength(r, font=font)) / 2, y), r, font=font, fill='white',
                        stroke_width=STROKE, stroke_fill='black')
                y += SIZE + 3
            im.save(sub / f'{f:04d}.png')
        # jPSXdec frame = 0-based index = header frame - 1 (insert() asserts headers run 1..N); paths are cwd-relative
        xml = ''.join(f'  <replace frame="{f - 1}">{(sub / f"{f:04d}.png").as_posix()}</replace>\n'
                      for f in sorted(todo[n]))
        (d / 'replace.xml').write_text(f'<?xml version="1.0"?>\n<str-replace version="0.3">\n{xml}</str-replace>\n')
        print(n, len(todo[n]), 'frames')


JPSXDEC = ROOT / 'tools/jpsxdec/jpsxdec_v2.1-beta/jpsxdec.jar'
DONE = OUT / 'out'  # subtitled STRs by disc path; insert.py copies them into the overlay (re-encoding is slow)


def insert(names):
    """Re-encode the subtitled frames into a copy of each STR with jPSXdec -replaceframes -> work/fmv/out/<disc path>."""
    for n, p in movies(names or sorted({m for m, *_ in lines()})):
        rel = p.relative_to(TREE)
        dst = DONE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(p.read_bytes())
        idx = OUT / n / 'jpsxdec.idx'
        jar = ['java', '-jar', str(JPSXDEC)]
        # cwd: jPSXdec writes index.log / replace.log there; every path passed is absolute
        subprocess.run(jar + ['-f', str(dst), '-x', str(idx)], check=True, stdout=subprocess.DEVNULL, cwd=OUT / n)
        video = next(r for r in idx.read_text().splitlines() if r.startswith('#:0|') and 'Type:Video' in r)
        count = video.split('Frame Count:')[1].split('|')[0]
        assert f'Header Frames:1-{count}' in video, video  # so frame index = header frame - 1 (burn's XML)
        subprocess.run(jar + ['-x', str(idx), '-i', '0', '-replaceframes', str(OUT / n / 'replace.xml')],
                       check=True, stdout=subprocess.DEVNULL, cwd=OUT / n)
        bad = check(p.read_bytes(), dst.read_bytes(), n)
        assert not bad, bad
        print(n, 'ok')


def check(old, new, name):
    """Problems with a patched STR: size, any sector header or audio sector changed, or video changed in a frame
    no subtitle covers (diffcheck.py)."""
    if len(old) != len(new):
        return [f'{name}: size {len(old)} -> {len(new)}']
    frames = {f for m, a, b, _ in lines() if m == name for f in range(a, b + 1)}
    bad = []
    for i in range(0, len(old), 2336):
        if old[i:i + 2336] == new[i:i + 2336]:
            continue
        video = old[i + 8:i + 12] == b'\x60\x01\x01\x80'
        fno = struct.unpack_from('<I', old, i + 16)[0] if video else None
        if old[i:i + 8] != new[i:i + 8] or not video or new[i + 8:i + 20] != old[i + 8:i + 20] or fno not in frames:
            bad.append(f'{name}: sector {i // 2336} (frame {fno}) changed outside a subtitle')
    return bad


if __name__ == '__main__':
    cmd, *args = sys.argv[1:] or ['-h']
    {'extract': extract, 'transcribe': transcribe, 'collect': collect, 'retime': retime, 'merge': merge, 'burn': burn, 'insert': insert}.get(
        cmd, lambda _: print(__doc__))(args)
