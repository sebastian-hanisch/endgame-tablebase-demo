"""König+Turm gegen König (KTK) - die klassische Tablebase-Stellung (Ken
Thompsons erste vollständig berechnete Schach-Tablebase, 1986). Nur die für
dieses eine Endspiel nötigen Schachregeln, nicht ein allgemeiner Schach-Engine.

Felder sind Ganzzahlen 0-63 (rank*8+file, rank/file je 0-7 = Reihe 1-8/Linie
a-h). Weiß hat König+Turm, Schwarz nur den König - WEISS versucht matt zu
setzen, SCHWARZ versucht zu überleben (Remis: Patt oder den Turm schlagen).
"""

from __future__ import annotations

from dataclasses import dataclass

WHITE = 1
BLACK = -1

_KING_DELTAS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
_ROOK_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def square(file: int, rank: int) -> int:
    return rank * 8 + file


def file_of(sq: int) -> int:
    return sq % 8


def rank_of(sq: int) -> int:
    return sq // 8


def on_board(file: int, rank: int) -> bool:
    return 0 <= file < 8 and 0 <= rank < 8


@dataclass(frozen=True)
class Position:
    white_king: int
    white_rook: int | None  # None = Turm bereits geschlagen (totes Remis)
    black_king: int
    side_to_move: int  # WHITE oder BLACK


def _king_targets(sq: int) -> list[int]:
    f, r = file_of(sq), rank_of(sq)
    targets = []
    for df, dr in _KING_DELTAS:
        nf, nr = f + df, r + dr
        if on_board(nf, nr):
            targets.append(square(nf, nr))
    return targets


def kings_adjacent(a: int, b: int) -> bool:
    return abs(file_of(a) - file_of(b)) <= 1 and abs(rank_of(a) - rank_of(b)) <= 1


def _rook_targets(sq: int, blockers: set[int]) -> list[int]:
    f, r = file_of(sq), rank_of(sq)
    targets = []
    for df, dr in _ROOK_DIRECTIONS:
        nf, nr = f + df, r + dr
        while on_board(nf, nr):
            t = square(nf, nr)
            targets.append(t)
            if t in blockers:
                break
            nf += df
            nr += dr
    return targets


def rook_attacks(rook_sq: int | None, blockers: set[int]) -> set[int]:
    """Felder, die der Turm bestreicht (blockers OHNE das eigene Turmfeld,
    inklusive der ersten blockierenden Figur selbst - die kann geschlagen
    werden, dahinter ist Schluss)."""
    if rook_sq is None:
        return set()
    return set(_rook_targets(rook_sq, blockers))


def is_legal_position(pos: Position) -> bool:
    """Grundlegende Aufstellungs-Legalität (keine Zug-Historie geprüft, nur
    ob die Stellung selbst überhaupt vorkommen könnte): Felder verschieden,
    Turm nicht auf einem Königsfeld, Könige nicht benachbart."""
    if pos.white_king == pos.black_king:
        return False
    if pos.white_rook is not None and pos.white_rook in (pos.white_king, pos.black_king):
        return False
    if kings_adjacent(pos.white_king, pos.black_king):
        return False
    return True


def is_check(pos: Position) -> bool:
    """Nur Schwarz kann im Schach stehen (nur Weiß hat einen Turm)."""
    if pos.white_rook is None:
        return False
    blockers = {pos.white_king, pos.black_king}
    return pos.black_king in rook_attacks(pos.white_rook, blockers - {pos.black_king})


def legal_moves(pos: Position) -> list[Position]:
    """Alle legalen Folgestellungen (nicht die Züge selbst - für Retrograde-
    Analyse reichen die Folgestellungen)."""
    if pos.side_to_move == WHITE:
        return _white_moves(pos)
    return _black_moves(pos)


def _white_moves(pos: Position) -> list[Position]:
    moves = []
    # Koenigszuege
    for t in _king_targets(pos.white_king):
        if t == pos.white_rook:
            continue
        if kings_adjacent(t, pos.black_king):
            continue
        moves.append(Position(t, pos.white_rook, pos.black_king, BLACK))
    # Turmzuege
    if pos.white_rook is not None:
        blockers = {pos.white_king, pos.black_king}
        for t in _rook_targets(pos.white_rook, blockers):
            if t == pos.white_king:
                continue
            if t == pos.black_king:
                continue  # Turm kann den Koenig nie wirklich schlagen (Schach waere vorher aufgeloest)
            moves.append(Position(pos.white_king, t, pos.black_king, BLACK))
    return moves


def _black_moves(pos: Position) -> list[Position]:
    moves = []
    rook_blockers = {pos.white_king, pos.black_king}
    attacked_ignoring_own_king = rook_attacks(pos.white_rook, rook_blockers - {pos.black_king})
    for t in _king_targets(pos.black_king):
        if t == pos.white_king or kings_adjacent(t, pos.white_king):
            continue
        if t == pos.white_rook:
            # Turm schlagen: nur legal, wenn der Turm dort nicht vom weissen
            # Koenig gedeckt wird.
            if kings_adjacent(pos.white_king, t):
                continue
            moves.append(Position(pos.white_king, None, t, WHITE))
            continue
        if t in attacked_ignoring_own_king:
            continue
        moves.append(Position(pos.white_king, pos.white_rook, t, WHITE))
    return moves


def is_terminal(pos: Position) -> tuple[bool, str | None]:
    """Gibt (ist_terminal, ergebnis) zurück. ergebnis in {"matt", "patt",
    "turm_geschlagen", None}. "matt" = Sieg Weiß, alles andere Remis."""
    if pos.white_rook is None:
        return True, "turm_geschlagen"
    moves = legal_moves(pos)
    if moves:
        return False, None
    if pos.side_to_move == BLACK and is_check(pos):
        return True, "matt"
    return True, "patt"
