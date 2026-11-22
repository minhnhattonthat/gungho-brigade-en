"""release.py: gate, build and package one release -> release/Gungho_Brigade_EN_v<ver>.zip (xdelta patch + README.txt).

    python -X utf8 tools/release.py [--version 1.0] [--force] [--no-build]

Stops at the first failure: insert + build -> tests (tools/check.py) -> smoke boot -> jp_left (every text file, known
runs in docs/jp_known/) -> qa_gate check on every work/qa/**/manifest.tsv -> textcover -> no unticked docs/polish.md
line -> no template placeholder in README.md -> debug tool off -> xdelta3 patch -> re-apply to the clean .bin and
compare -> zip (ZIP_STORED). Refuses to overwrite an existing version without --force. Never publishes.

Debug tool off: the debug tool is Lua run by the emulator (tools/debug/warp.lua), never written into the disc; the
check is that build.py's diffcheck (changed bytes only in text, pointer, font and graphics ranges) passed for this
build and that no debug Lua or memory card is among the patched files.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
ORIG = ROOT / "rom/Gungho Brigade (Japan).bin"
BUILT = ROOT / "build/gungho_en.bin"
FILES = ROOT / "work/build/files"
TREE = ROOT / "work/disc/tree"
JP_FILES = ["GUNHO.EXE", "MENU.EXE", "MENUMV.EXE", "ENDING.BIN", "SLPS_019.02", "TABLE.BIN", "SCENFILE.DAT",
            "TABLE/MENU.DAT", "TABLE/OVTABLE.DAT"]
TEXTCOVER = ["work/qa/tour", "work/qa/tour/scen_strings.tsv", "--waive", "docs/text_unshown.tsv"]


def step(name, cmd):
    print(f"== {name}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"FAILED: {name} (exit {r.returncode})")


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def crc32(path):
    c = 0
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            c = zlib.crc32(b, c)
    return f"{c:08X}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    ap.add_argument("--no-build", action="store_true", help="gate and package the current build/ (no insert/build)")
    a = ap.parse_args()

    out = ROOT / "release"
    stem = f"Gungho_Brigade_EN_v{a.version}"
    patch, zpath = out / f"{stem}.xdelta", out / f"{stem}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"{zpath.name} or {patch.name} exists; pass --force to overwrite")

    step("rom check", PY + ["tools/check_rom.py"])
    if not a.no_build:
        step("insert", PY + ["tools/insert.py"])
        step("build (incl. diffcheck)", PY + ["build.py"])
    step("tests", PY + ["tools/check.py"])
    step("smoke", PY + [f"{SKILL}/scripts/emu.py", "build/gungho_en.cue", "--out", "work/qa/smoke", "--route",
                        "tools/routes/boot.txt", "--smoke"])
    for f in JP_FILES:
        known = ROOT / "docs/jp_known" / (f.replace("/", "_") + ".txt")
        step(f"jp_left {f}", PY + [f"{SKILL}/scripts/jp_left.py", str(FILES / f), "--orig", str(TREE / f), "--sjis"]
             + (["--known", str(known)] if known.exists() else []))
    manifests = sorted((ROOT / "work/qa").rglob("manifest.tsv"))
    if not manifests:
        sys.exit("FAILED: no work/qa/**/manifest.tsv")
    for m in manifests:
        step(f"qa_gate {m.parent.relative_to(ROOT)}", PY + [f"{SKILL}/scripts/qa_gate.py", "check", str(m),
                                                            str(m.parent / "verdicts")])
    # coverage list = this build's stage-string keys (keys change with every digraph renumbering)
    rows = (ROOT / "build/strings.tsv").read_text(encoding="utf-8").splitlines()
    (ROOT / TEXTCOVER[1]).write_text("".join(r + "\n" for r in rows if re.match(r"s\d\d_", r)), encoding="utf-8",
                                     newline="\n")
    step("textcover", PY + [f"{SKILL}/scripts/textcover.py"] + TEXTCOVER)

    print("== polish / README / debug", flush=True)
    open_lines = [l for l in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines() if l.startswith("- [ ]")]
    if open_lines:
        sys.exit(f"FAILED: {len(open_lines)} unticked line(s) in docs/polish.md")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    holes = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game)>|<[A-Z][a-z]+ /", readme)
    if holes:
        sys.exit(f"FAILED: template placeholders in README.md: {holes}")
    sha1 = digest(ORIG, "sha1")
    zip_readme = (ROOT / "docs/release-README.txt").read_text(encoding="utf-8")
    for doc, name in ((readme, "README.md"), (zip_readme, "docs/release-README.txt")):
        if sha1 not in doc:
            sys.exit(f"FAILED: {name} lacks the base image SHA-1 {sha1}")
    debug = [p for p in FILES.rglob("*") if p.suffix.lower() in (".lua", ".mcd", ".sstate")]
    if debug:
        sys.exit(f"FAILED: debug files in the build: {debug}")

    out.mkdir(exist_ok=True)
    print(f"== xdelta3 -> {patch.name}", flush=True)
    patch.unlink(missing_ok=True)
    step("xdelta3 encode", ["xdelta3", "-e", "-9", "-B", str(ORIG.stat().st_size), "-s", str(ORIG), str(BUILT),
                            str(patch)])
    check = out / "reapplied.bin"
    check.unlink(missing_ok=True)
    step("xdelta3 re-apply", ["xdelta3", "-d", "-B", str(ORIG.stat().st_size), "-s", str(ORIG), str(patch), str(check)])
    built_sha1 = digest(BUILT, "sha1")
    if digest(check, "sha1") != built_sha1:
        sys.exit("FAILED: re-applied patch differs from build/gungho_en.bin")
    check.unlink()

    text = (zip_readme.replace("{VERSION}", a.version).replace("{PATCH}", patch.name)
            .replace("{PATCHED_SHA1}", built_sha1).replace("{PATCHED_CRC32}", crc32(BUILT)))
    if re.search(r"\{[A-Z_0-9]+\}", text):
        sys.exit("FAILED: unfilled {FIELD} in docs/release-README.txt")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    print(f"OK {zpath.relative_to(ROOT)}: {patch.name} ({patch.stat().st_size:,} B) + README.txt; "
          f"patched sha1 {built_sha1}")


if __name__ == "__main__":
    main()
