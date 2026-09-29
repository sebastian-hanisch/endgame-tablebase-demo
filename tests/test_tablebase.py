"""Tablebase-Nachschlag gegen dieselben von Hand verifizierten Stellungen wie
tests/test_chess.py - muss exakt übereinstimmen, jetzt per Array-Zugriff
statt Live-Suche."""

from eg_chess import BLACK, WHITE, Position, square
from eg_tablebase import best_moves, lookup


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_mate_position_has_dtm_zero():
    mate = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)
    out = lookup(mate)
    assert out.result == "win"
    assert out.dtm == 0


def test_stalemate_position_is_draw():
    pos = Position(sq("c", 1), sq("b", 2), sq("a", 1), BLACK)
    out = lookup(pos)
    assert out.result == "draw"


def test_position_without_rook_is_always_draw():
    pos = Position(sq("c", 1), None, sq("a", 1), WHITE)
    out = lookup(pos)
    assert out.result == "draw"


def test_mate_in_one_parent_has_dtm_one():
    parent = Position(sq("c", 7), sq("h", 1), sq("a", 8), WHITE)
    out = lookup(parent)
    assert out.result == "win"
    assert out.dtm == 1
    mate = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)
    assert mate in best_moves(parent)


def test_best_moves_for_white_all_share_the_minimum_dtm():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    moves = best_moves(pos)
    assert moves
    dtms = {lookup(m).dtm for m in moves}
    assert len(dtms) == 1


def test_best_moves_for_black_prefers_draw_over_any_win():
    # Wenn Schwarz eine Remis-Fortsetzung hat, muss best_moves NUR Remis-Züge
    # liefern, auch wenn andere Züge (langsamere) Siege für Weiss waeren.
    pos = Position(sq("h", 8), sq("a", 2), sq("a", 1), BLACK)
    moves = best_moves(pos)
    assert moves
    assert all(lookup(m).result == "draw" for m in moves)
