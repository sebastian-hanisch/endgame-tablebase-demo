"""Eine bewusst naive Heuristik (Königsabstand verkleinern, Turm ignorieren)
als Gegenstück zur exakten Tablebase - der Bewertungsfunktionen-Hook dieses
Stücks: wo weicht "gesunder Menschenverstand" vom exakt bewiesenen Optimum ab?
"""

from __future__ import annotations

from eg_chess import WHITE, Position, file_of, legal_moves, rank_of
from eg_tablebase import best_moves, lookup


def chebyshev_distance(a: int, b: int) -> int:
    return max(abs(file_of(a) - file_of(b)), abs(rank_of(a) - rank_of(b)))


def move_destination(pos: Position, child: Position) -> int:
    """Das Feld, auf das die tatsächlich gezogene Figur gelangt ist (für
    Weiß: König ODER Turm - je nachdem, was sich geändert hat)."""
    if pos.side_to_move == WHITE:
        if child.white_king != pos.white_king:
            return child.white_king
        return child.white_rook
    return child.black_king


def heuristic_move(pos: Position) -> Position | None:
    """Naive Heuristik: wähle den Zug, der den Königsabstand am stärksten
    verkleinert (Standard-Lehrbuchidee "König heranführen") - IGNORIERT dabei
    vollständig, was der Turm gerade bewirkt."""
    children = legal_moves(pos)
    if not children:
        return None
    if pos.side_to_move == WHITE:
        return min(children, key=lambda c: chebyshev_distance(c.white_king, c.black_king))
    return max(children, key=lambda c: chebyshev_distance(c.white_king, c.black_king))


def format_de_number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}".replace(",", ".")


def dtm_verdict(pos: Position) -> str:
    outcome = lookup(pos)
    mover = "Weiß" if pos.side_to_move == WHITE else "Schwarz"
    if outcome.result == "draw":
        return f"Theoretisches Remis (perfektes Spiel beider Seiten) - {mover} am Zug."
    full_moves = (outcome.dtm + 1) // 2
    return f"Weiß erzwingt Matt in {full_moves} Zügen ({outcome.dtm} Halbzüge) - {mover} am Zug."
