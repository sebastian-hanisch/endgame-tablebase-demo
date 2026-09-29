"""PRESETS, Permalink (Begrenzen/Einrasten), Session-Defaults."""

from __future__ import annotations

import streamlit as st

from eg_chess import BLACK, WHITE, Position, is_legal_position, square

PRESETS = {
    "Rückrand-Matt (Weiß am Zug, 1 vor Matt)": {"wk": "c7", "wr": "h1", "bk": "a8", "stm": WHITE},
    "Lehrbuch-Start (weit weg, Weiß gewinnt)": {"wk": "a1", "wr": "d4", "bk": "h8", "stm": WHITE},
    "Fast Patt-Falle (Schwarz am Zug)": {"wk": "c1", "wr": "b2", "bk": "a1", "stm": BLACK},
}
PRESET_HELP = {
    "Rückrand-Matt (Weiß am Zug, 1 vor Matt)": "Turm h1-a1 setzt sofort matt - von Hand nachvollziehbar.",
    "Lehrbuch-Start (weit weg, Weiß gewinnt)": "Königen und Turm in den Ecken - der Lehrbuch-Anfang.",
    "Fast Patt-Falle (Schwarz am Zug)": "Echtes Patt-Beispiel - kein Matt, obwohl Schwarz keinen Zug mehr hat.",
}

_DEFAULT = PRESETS["Lehrbuch-Start (weit weg, Weiß gewinnt)"]


def _parse_square(text: str) -> int | None:
    text = text.strip().lower()
    if len(text) != 2 or text[0] not in "abcdefgh" or text[1] not in "12345678":
        return None
    return square(ord(text[0]) - ord("a"), int(text[1]) - 1)


def preset_position(preset: dict) -> Position:
    return Position(_parse_square(preset["wk"]), _parse_square(preset["wr"]), _parse_square(preset["bk"]), preset["stm"])


def apply_preset(name: str) -> None:
    st.session_state["position"] = preset_position(PRESETS[name])


def init_session_state_defaults() -> None:
    if "position" not in st.session_state:
        st.session_state["position"] = preset_position(_DEFAULT)


def load_permalink_settings() -> None:
    """Lädt die Stellung aus der URL - NUR beim allerersten Lauf dieser
    Session (sonst würde jeder Zugklick sofort wieder rückgängig gemacht -
    echter, bereits einmal gefundener Bug in minimax-demo, siehe dortige
    Moduldoku)."""
    if "position" in st.session_state:
        return
    params = st.query_params
    if not all(k in params for k in ("wk", "wr", "bk", "stm")):
        return
    wk = _parse_square(params["wk"])
    wr = None if params["wr"] == "-" else _parse_square(params["wr"])
    bk = _parse_square(params["bk"])
    stm = WHITE if params["stm"] == "w" else BLACK
    if wk is None or bk is None or (params["wr"] != "-" and wr is None):
        return
    pos = Position(wk, wr, bk, stm)
    if not is_legal_position(pos):
        return
    st.session_state["position"] = pos


def square_name(sq: int | None) -> str:
    if sq is None:
        return "-"
    return "abcdefgh"[sq % 8] + str(sq // 8 + 1)


def sync_query_params(pos: Position) -> None:
    st.query_params["wk"] = square_name(pos.white_king)
    st.query_params["wr"] = square_name(pos.white_rook)
    st.query_params["bk"] = square_name(pos.black_king)
    st.query_params["stm"] = "w" if pos.side_to_move == WHITE else "b"
