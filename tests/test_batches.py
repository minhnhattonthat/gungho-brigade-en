import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches as b  # noqa: E402


def _mk(jp, form="dlg"):
    e = dict(id="t", max="99", jp=jp, en="", notes="", form=form, speaker="", sep="", pre="", post="")
    m = b.SPEAKER.match(jp)
    if m:
        e["speaker"], e["sep"], jp = m[1], m[2], jp[m.end():]
    return e


def test_compose_speaker_wrap_and_lint():
    e = _mk("オールドマン/「明朝５時をもって」")
    out = b.compose(e, '"' + "word " * 20 + '"', {"オールドマン": "Oldman"})
    lines = out.split("/")
    assert lines[0] == "Oldman" and all(len(ln) <= 42 for ln in lines)
    assert "3 lines" not in " ".join(b.width_problems(e, out))
    long = b.compose(e, "word " * 30, {"オールドマン": "Oldman"})
    assert any("box holds 3" in p for p in b.width_problems(e, long))


def test_shipped_english_lint_clean():
    assert b.main(["check"]) == 0  # every merged line: width, lines, glyphs, glossary, honorifics


def test_inline_speaker_and_tokens():
    e = _mk("審判「ただし」")
    assert b.compose(e, '"However."', {"審判": "Referee"}) == 'Referee: "However."'
    g = _mk("%d ﾉ ﾀﾞﾒｰｼﾞ ", "name")
    assert any("control codes" in p for p in b.problems(g, "damage", []))
    assert not b.problems(g, "%d damage", [])


def test_save_title_digits_stay_put():
    """The game writes stage/time digits at fixed offsets into the card save titles."""
    import insert
    rows = {r["id"]: r for r in b.x.read_tsv(b.SCRIPT / "table.tsv")}
    for sid in insert.SAVE_TITLES:
        jp, en = rows[sid]["jp"], insert.to_full(rows[sid]["en"] or rows[sid]["jp"])
        assert len(en) == len(jp), sid
        assert [i for i, c in enumerate(jp) if c == "０"] == [i for i, c in enumerate(en) if c == "０"], sid


def test_full_breaks_keep_empty_lines():
    e = _mk("上書き？{n}{n}上書きする時は", "full")
    assert b.compose(e, "Overwrite? / / To overwrite, 1/3") == "Overwrite?{n}{n}To overwrite, 1/3"
