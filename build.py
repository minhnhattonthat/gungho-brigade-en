"""build.py: rebuild the disc with every patched file swapped in -> build/gungho_en.bin + .cue.

    python -X utf8 build.py [--overlay DIR] [--out build/gungho_en.bin]

Checks the dump against rom.sha1, unpacks it once (dumpsxiso -> work/disc/tree + layout.xml; the tree stays
pristine), then runs mkpsxiso on a copy of layout.xml where each file that exists under the overlay dir
(work/build/files/<disc path>, e.g. work/build/files/MOVIE/X.STR) is taken from there instead. Insert steps
write their patched files into the overlay; with an empty overlay the output is byte-identical to the dump
(tests/test_build.py). Files are found by ISO name (CdSearchFile), so a patched file may change size.
"""
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from check_rom import check  # noqa: E402

CUE = ROOT / "rom/Gungho Brigade (Japan).cue"
DISC = ROOT / "work/disc"
MKPSXISO = ROOT / "tools/mkpsxiso/mkpsxiso-2.30-win64"
OVERLAY = ROOT / "work/build/files"
OUT = ROOT / "build/gungho_en.bin"


def unpack():
    if (DISC / "layout.xml").exists() and (DISC / "tree/SYSTEM.CNF").exists():
        return
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(MKPSXISO / "dumpsxiso.exe"), "-x", "tree", "-s", "layout.xml", str(CUE)],
                   cwd=DISC, check=True)


def layout(overlay, dest):
    """Write a layout with absolute sources, overlay files replacing tree files. Returns the overridden disc paths."""
    tree = ET.parse(DISC / "layout.xml")
    lic = tree.find(".//license")
    lic.set("file", str((DISC / lic.get("file")).resolve()))
    dtree = tree.find(".//directory_tree")
    dtree.set("source", str((DISC / dtree.get("source")).resolve()))
    used = []

    def walk(node, path):
        for el in node:
            if el.tag == "dir":
                walk(el, path + [el.get("name")])
            elif el.tag == "file":
                rel = "/".join(path + [el.get("name")])
                if (overlay / rel).is_file():
                    el.set("source", str((overlay / rel).resolve()))
                    used.append(rel)
    walk(dtree, [])
    extra = sorted(p.relative_to(overlay).as_posix() for p in overlay.rglob("*") if p.is_file()) if overlay.is_dir() else []
    unknown = [p for p in extra if p not in used]
    if unknown:
        sys.exit(f"overlay files not on the disc: {unknown}")
    tree.write(dest, encoding="utf-8", xml_declaration=True)
    return used


def build(out=OUT, overlay=OVERLAY):
    check()
    unpack()
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    xml = out.with_suffix(".xml")
    used = layout(Path(overlay), xml)
    r = subprocess.run([str(MKPSXISO / "mkpsxiso.exe"), "-y", "-q", "-o", str(out), "-c", str(out.with_suffix(".cue")),
                        str(xml)], capture_output=True, text=True, errors="replace")
    if r.returncode or not out.exists():
        sys.exit(f"mkpsxiso failed (close any emulator holding {out.name}):\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
    xml.unlink()
    return out, used


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--overlay", default=str(OVERLAY))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    if Path(a.overlay).resolve() == OVERLAY.resolve() and OVERLAY.is_dir():
        import diffcheck  # every changed byte inside an allowed text/font range (the per-file romdiff)
        if diffcheck.main():
            sys.exit("diffcheck failed: the overlay writes outside its allowed ranges")
    out, used = build(a.out, a.overlay)
    print(f"{out} ({len(used)} patched file(s): {', '.join(used) or 'none'})")


if __name__ == "__main__":
    main()
