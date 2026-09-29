"""Lädt die vorab berechnete Tablebase (siehe tools/build_tablebase.py) und
schlägt Stellungen als reinen Array-Zugriff nach - kein Live-Suchlauf."""

from __future__ import annotations

import array
from dataclasses import dataclass
from functools import lru_cache

from eg_chess import WHITE, Position, legal_moves
from eg_constants import DATA_PATH


@dataclass(frozen=True)
class Outcome:
    result: str  # "win" oder "draw"
    dtm: int | None


def _encode_index(wk: int, wr: int, bk: int, side_to_move: int) -> int:
    return ((wk * 64 + wr) * 64 + bk) * 2 + (0 if side_to_move == WHITE else 1)


@lru_cache(maxsize=1)
def _load_table() -> array.array:
    table = array.array("H")
    with open(DATA_PATH, "rb") as f:
        table.frombytes(f.read())
    return table


def lookup(pos: Position) -> Outcome:
    if pos.white_rook is None:
        return Outcome("draw", None)
    table = _load_table()
    raw = table[_encode_index(pos.white_king, pos.white_rook, pos.black_king, pos.side_to_move)]
    if raw == 0:
        return Outcome("draw", None)
    return Outcome("win", raw - 1)


def best_moves(pos: Position) -> list[Position]:
    """Alle Folgestellungen, die den Matt-Abstand optimal fortsetzen (für
    Weiß: schnellstmögliches Matt; für Schwarz: längstmöglicher Widerstand,
    oder ein Remis, falls erreichbar)."""
    children = legal_moves(pos)
    if not children:
        return []
    outcomes = [(c, lookup(c)) for c in children]
    if pos.side_to_move == WHITE:
        draws = [c for c, o in outcomes if o.result == "draw"]
        wins = [(c, o.dtm) for c, o in outcomes if o.result == "win"]
        if wins:
            best_dtm = min(d for _, d in wins)
            return [c for c, d in wins if d == best_dtm]
        return draws
    else:
        draws = [c for c, o in outcomes if o.result == "draw"]
        if draws:
            return draws
        wins = [(c, o.dtm) for c, o in outcomes if o.result == "win"]
        best_dtm = max(d for _, d in wins)
        return [c for c, d in wins if d == best_dtm]
