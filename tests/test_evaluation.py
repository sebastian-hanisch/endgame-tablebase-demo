"""Naive Heuristik + Zug-Beschreibungs-Hilfen."""

from eg_chess import BLACK, WHITE, Position, square
from eg_evaluation import chebyshev_distance, dtm_verdict, heuristic_move, move_destination


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_chebyshev_distance_same_square_is_zero():
    assert chebyshev_distance(sq("a", 1), sq("a", 1)) == 0


def test_chebyshev_distance_diagonal():
    assert chebyshev_distance(sq("a", 1), sq("d", 4)) == 3


def test_heuristic_move_reduces_king_distance_for_white():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    move = heuristic_move(pos)
    before = chebyshev_distance(pos.white_king, pos.black_king)
    after = chebyshev_distance(move.white_king, move.black_king)
    assert after <= before


def test_move_destination_identifies_king_move():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    child = Position(sq("b", 1), sq("h", 1), sq("h", 8), BLACK)
    assert move_destination(pos, child) == sq("b", 1)


def test_move_destination_identifies_rook_move():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    child = Position(sq("a", 1), sq("h", 4), sq("h", 8), BLACK)
    assert move_destination(pos, child) == sq("h", 4)


def test_move_destination_for_black_king_move():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), BLACK)
    child = Position(sq("a", 1), sq("h", 1), sq("g", 8), WHITE)
    assert move_destination(pos, child) == sq("g", 8)


def test_dtm_verdict_mentions_draw_for_stalemate():
    pos = Position(sq("c", 1), sq("b", 2), sq("a", 1), BLACK)
    assert "Remis" in dtm_verdict(pos)


def test_dtm_verdict_mentions_zuege_for_win():
    pos = Position(sq("c", 7), sq("h", 1), sq("a", 8), WHITE)
    assert "Matt" in dtm_verdict(pos)
