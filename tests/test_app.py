"""Rauchtests der Streamlit-Oberfläche per AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from eg_chess import BLACK, WHITE, Position, square
from eg_presets import PRESETS, preset_position

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=60)
    if setup is not None:
        setup(at)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Stellung" in h.value for h in at.subheader)


def test_every_preset_renders():
    for name in PRESETS:

        def setup(at, name=name):
            at.session_state["position"] = preset_position(PRESETS[name])

        _run(setup)


def test_terminal_position_shows_no_move_selector():
    def setup(at):
        at.session_state["position"] = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)

    at = _run(setup)
    assert not any(sb.label.startswith("Legale Züge") for sb in at.selectbox)


def test_executing_a_move_updates_the_position():
    def setup(at):
        at.session_state["position"] = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)

    at = _run(setup)
    before = at.session_state["position"]
    buttons = [b for b in at.button if b.label == "Zug ausführen"]
    assert buttons
    buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["position"] != before


def test_permalink_restores_position():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["wk"] = "c7"
    at.query_params["wr"] = "a1"
    at.query_params["bk"] = "a8"
    at.query_params["stm"] = "b"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    pos = at.session_state["position"]
    assert pos.white_king == sq("c", 7)
    assert pos.white_rook == sq("a", 1)
    assert pos.black_king == sq("a", 8)
    assert pos.side_to_move == BLACK


def test_permalink_does_not_get_clobbered_by_later_rerun():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["wk"] = "a1"
    at.query_params["wr"] = "h1"
    at.query_params["bk"] = "h8"
    at.query_params["stm"] = "w"
    at.run()
    before = at.session_state["position"]
    buttons = [b for b in at.button if b.label == "Zug ausführen"]
    buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["position"] != before
