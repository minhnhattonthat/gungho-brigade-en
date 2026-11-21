"""Phase 8 dialogue tour: show every stage-overlay string in the real dialogue box, one shot per page, with text
coverage logged (tools/lua/forcetext.lua + tools/lua/textcover.lua over tools/debug/warp.lua).

    python -X utf8 tools/tour.py [s08 s14 ..] [--cue build/gungho_en.cue] [--jobs 3] [--out work/qa/tour]

Per stage: cold boot -> warp to the stage (NEW GAME path, intro event 9); the intro's first dialogue call is
re-entered once per listed string (all pointer-table strings of the built overlay, in table order), then the intro
plays on to battle start. Output <out>/<stage>/: t_<n>_<id>_p<page>.png, log.txt (FORCE / TEXT lines), list.txt;
contact sheets <out>/<stage>_sheet*.png (sheet.py: the dialogue box cropped, 40 per page, full size). Exit 1 if a stage didn't show its whole
list or didn't arrive. Run tools/insert.py + build.py first: addresses come from work/build/files.
Coverage: textcover.py <out> build/strings.tsv (the run's copy is kept as <out>/strings.tsv).
"""
import argparse
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as x  # noqa: E402
from skill import SKILL  # noqa: E402

ROOT = x.ROOT
BUILT = ROOT / "work/build/files"
BLANK = ROOT / "work/saves/blank.mcd"
MASH = 60   # frames per circle press: a full 42x3 box has typed out by then (checked on the s08 tour)


def stage_lists(built=BUILT):
    """{stage: [(id, RAM address in the built overlay)]}, ids from the original overlay, matched by table slot."""
    dat0, offs0, ends0 = x.scen_entries(x.TREE)
    dat1, offs1, ends1 = x.scen_entries(built)
    out = {}
    for e, xo in x.OVERLAYS.items():
        _, stage, tgt0, _ = x.scen_overlay(dat0, offs0[e], ends0[e], xo)
        ovl1 = dat1[offs1[e] + xo:ends1[e]]
        t0, t1 = x.pointer_table(ovl1)
        ptrs = list(struct.unpack_from(f"<{(t1 - t0) // 4}I", ovl1, t0))
        assert len(ptrs) == sum(len(v) for v in tgt0.values()), f"s{stage:02d}: pointer table length changed"
        out[stage] = [(f"s{stage:02d}_{o:04x}", ptrs[tgt0[o][0]]) for o in sorted(tgt0) if (stage, o) not in x.SCEN_DATA]
    return out


def run(stage, items, cue, out):
    d = out / f"s{stage:02d}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    lst = d / "list.txt"
    lst.write_text("".join(f"{i} {a:08X}\n" for i, a in items), encoding="utf-8")
    frames = 16000 + len(items) * 3 * MASH
    cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(cue), "--out", str(d), "--sav", str(BLANK),
           "--debugger", "--frames", str(frames), "--timeout", "5400",
           "--script", str(ROOT / "tools/debug/warp.lua"), "--var", f"STAGE={stage}", "--var", f"MASH_EVERY={MASH}",
           "--script", str(ROOT / "tools/lua/forcetext.lua"), "--var", f"TEXT_LIST='{lst.as_posix()}'",
           "--script", str(ROOT / "tools/lua/textcover.lua")]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    forced = log.count("FORCE ")
    ok = p.returncode == 0 and "force: done" in log and "arrived" in log and forced == len(items)
    shots = sorted(d.glob("t_*.png"))
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", f"{SKILL}/scripts/sheet.py", *map(str, shots), "--crop", "20,16,280,66", "--cols", "5", "--max", "40", "--div", "1",
                        "--out", str(out / f"s{stage:02d}_sheet.png")], capture_output=True)
    return stage, ok, f"{forced}/{len(items)} forced, exit {p.returncode}, {len(shots)} shots"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stages", nargs="*", help="sNN (default: all 36)")
    ap.add_argument("--cue", default=str(ROOT / "build/gungho_en.cue"))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "work/qa/tour"))
    a = ap.parse_args()
    lists = stage_lists()
    want = [int(s.lstrip("s")) for s in a.stages] or sorted(lists)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "build/strings.tsv", out / "strings.tsv")
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda s: run(s, lists[s], a.cue, out), want))
    for stage, ok, info in results:
        print(f"{'ok  ' if ok else 'FAIL'} s{stage:02d}: {info}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
