"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Runs every tests/test_*.py through pytest. Slow tests (disc rebuild, emulator) are marked `slow`
and skipped here; run them with `python -X utf8 -m pytest -m slow`."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-m", "not slow", str(ROOT / "tests")], cwd=ROOT)
    # pytest exit 5 = no tests collected; that is fine only before any test exists
    sys.exit(0 if r.returncode == 5 and not list((ROOT / "tests").glob("test_*.py")) else r.returncode)
