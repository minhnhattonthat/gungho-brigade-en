"""tlshow.py id..: batch body + JP for each id (finds its work/tl batch). Run from the repo root; pairs with
tl_patch.py when rewording rows (e.g. to fit a SCENFILE region, see stagerows.py)."""
import sys, glob
want = set(sys.argv[1:])
for f in sorted(glob.glob("work/tl/b*.out.tsv")):
    b = f.split("\\")[-1].split("/")[-1][:4]
    src = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(f"work/tl/{b}.tsv", encoding="utf8")}
    for l in open(f, encoding="utf8"):
        i, body = l.rstrip("\n").split("\t", 1)
        if i in want:
            print(f"{b} {i}\tJP: {src[i][-1]}\n\tEN: {body}")
