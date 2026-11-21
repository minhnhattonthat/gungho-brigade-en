"""Warp to scenes from a cold boot and save their states (phase-2 debug tool).

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--cue build/gungho_en.cue] [--jobs 3]
    python -X utf8 tools/debug/warp.py --all            # regenerate every state in work/states/
    python -X utf8 tools/debug/warp.py --list

Each scene (tools/debug/scenes.tsv) either boots cold through tools/debug/warp.lua (stage index + mode), or, with a
`base`, starts from that scene's saved state and plays a short route (menus). Output: work/qa/warp/<scene>/
(final.png, shots, log.txt), state work/states/<scene>.sstate, and work/qa/warp/sheet*.png of every final.png.
Exit 1 if any scene failed to arrive (warp.lua logs "arrived"; based scenes must finish their route).
Runs use a blank memory card copy (work/saves/blank.mcd), so the portable card beside the emulator is untouched.
"""
import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SCENES = ROOT / "tools/debug/scenes.tsv"
ORIG = ROOT / "rom/Gungho Brigade (Japan).cue"
BLANK = ROOT / "work/saves/blank.mcd"
TIMED_FRAMES = 7000


def blank_card():
    """A freshly formatted 128 KB PS1 memory card (header, 15 free directory frames, empty broken-sector list)."""
    card = bytearray(0x20000)

    def frame(i, data):
        f = bytearray(data.ljust(127, b"\0"))
        x = 0
        for b in f:
            x ^= b
        card[i * 128:(i + 1) * 128] = f + bytes([x])
    frame(0, b"MC")
    for i in range(1, 16):
        frame(i, b"\xa0\0\0\0\0\0\0\0\xff\xff")
    for i in range(16, 36):
        frame(i, b"\xff\xff\xff\xff\0\0\0\0\xff\xff")
    frame(63, b"MC")
    return bytes(card)


def load():
    with open(SCENES, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if not r["name"].startswith("#")]
    for r in rows:
        assert len(r) == 6 and None not in r.values(), f"scenes.tsv row has wrong column count: {r}"
    return {r["name"]: r for r in rows}


def run(scene, rows, cue):
    r = rows[scene]
    out = ROOT / "work/qa/warp" / scene
    state = ROOT / "work/states" / f"{scene}.sstate"
    cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(cue), "--out", str(out),
           "--sav", str(BLANK), "--state-out", str(state), "--timeout", "900"]
    if r["base"]:
        base = ROOT / "work/states" / f"{r['base']}.sstate"
        if not base.exists():
            return scene, False, f"base state missing: run {r['base']} first"
        cmd += ["--state-in", str(base), "--route-str", r["route"], "--shot-every", "60"]
    elif not r["stage"]:   # cold boot, route only (title screens)
        cmd += ["--route-str", r["route"], "--shot-every", "120"]
    else:
        # modes: battle (stop at battle start), clear (win after the intro, stop at the intermission),
        # ending (staff roll; timed), gameover (defeat event instead of the intro), timed (no arrival marker: run TIMED_FRAMES and stop)
        timed = r["mode"] in ("ending", "timed")
        cmd += ["--script", str(ROOT / "tools/debug/warp.lua"), "--var", f"STAGE={int(r['stage'])}",
                "--frames", str(TIMED_FRAMES if timed else 30000), "--shot-every", "300"]
        if r["mode"] in ("clear", "ending", "gameover"):
            cmd += ["--var", f"{r['mode'].upper()}=1"]
        if r["mode"] == "gameover":   # stop on the defeat line; a based scene presses circle for "Game over"
            cmd += ["--var", "NOMASH=1"]
        if timed:
            cmd += ["--var", "TOUR=1"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    want = "" if r["base"] or not r["stage"] else ("patched" if r["mode"] in ("ending", "timed") else "arrived")
    ok = p.returncode == 0 and want in log and state.exists()
    return scene, ok, (log.strip().splitlines() or [p.stdout[-300:] + p.stderr[-300:]])[-2:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cue", default=str(ORIG))
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    rows = load()
    if not BLANK.exists():
        BLANK.parent.mkdir(parents=True, exist_ok=True)
        BLANK.write_bytes(blank_card())
    if a.list:
        for r in rows.values():
            print(f"{r['name']:28} {r['notes']}")
        return 0
    names = list(rows) if a.all else a.scenes
    unknown = [n for n in names if n not in rows]
    if unknown or not names:
        ap.error(f"unknown or no scenes: {unknown}")
    # cold-boot scenes first (in parallel), then based scenes in file order (each needs its base's state)
    cold = [n for n in names if not rows[n]["base"]]
    based = [n for n in names if rows[n]["base"]]
    results = []
    with ThreadPoolExecutor(a.jobs) as ex:
        results += list(ex.map(lambda n: run(n, rows, a.cue), cold))
    for n in based:
        results.append(run(n, rows, a.cue))
    for scene, ok, info in results:
        print(f"{'ok  ' if ok else 'FAIL'} {scene}: {info}")
    finals = [str(ROOT / "work/qa/warp" / s / "final.png") for s, ok, _ in results
              if (ROOT / "work/qa/warp" / s / "final.png").exists()]
    if finals:
        subprocess.run([sys.executable, "-X", "utf8", f"{SKILL}/scripts/sheet.py", *finals,
                        "--out", str(ROOT / "work/qa/warp/sheet.png")], capture_output=True)
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
