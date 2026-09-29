"""König+Turm-gegen-König-Regeln: von Hand nachgerechnete Stellungen.

Die Schachbrett-Geometrie (Matt-/Patt-Beispiele) wurde per Handrechnung
(Nachbarfelder, Turm-Linien, Königsdeckung) UND unabhängig über eine
Brute-Force-Suche im eigenen Code gefunden, dann noch einmal von Hand
nachvollzogen (siehe Moduldoku/Commit) - kein öffentlicher Referenzlöser für
Schach-Endspiele in dieser Form verfügbar, deshalb doppelte Handrechnung
statt Kreuzprobe.
"""

from eg_chess import BLACK, WHITE, Position, is_check, is_legal_position, is_terminal, kings_adjacent, legal_moves, square


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_square_roundtrip():
    assert sq("a", 1) == 0
    assert sq("h", 8) == 63
    assert sq("e", 4) == square(4, 3)


def test_kings_adjacent_true_for_touching_squares():
    assert kings_adjacent(sq("e", 4), sq("e", 5))
    assert kings_adjacent(sq("e", 4), sq("f", 5))
    assert kings_adjacent(sq("e", 4), sq("e", 4))


def test_kings_adjacent_false_for_distant_squares():
    assert not kings_adjacent(sq("a", 1), sq("h", 8))
    assert not kings_adjacent(sq("e", 4), sq("e", 6))


def test_illegal_position_kings_adjacent():
    pos = Position(sq("e", 4), sq("a", 1), sq("e", 5), WHITE)
    assert not is_legal_position(pos)


def test_illegal_position_same_square():
    pos = Position(sq("e", 4), sq("a", 1), sq("e", 4), WHITE)
    assert not is_legal_position(pos)


def test_legal_position_kings_far_apart():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    assert is_legal_position(pos)


def test_open_position_has_many_legal_moves_and_is_not_terminal():
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    terminal, result = is_terminal(pos)
    assert not terminal
    assert result is None
    assert len(legal_moves(pos)) > 5


def test_back_rank_checkmate():
    # WK c7, WR a1, BK a8, Schwarz am Zug: Turm deckt die a-Linie (Schach),
    # a7 zusätzlich vom Turm gedeckt, b7/b8 vom weißen König - keine
    # Fluchtfelder, klassisches Turm-Matt.
    pos = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)
    assert is_check(pos)
    assert legal_moves(pos) == []
    terminal, result = is_terminal(pos)
    assert terminal
    assert result == "matt"


def test_stalemate_position():
    # WK c1, WR b2, BK a1, Schwarz am Zug: a1 selbst nicht angegriffen, aber
    # a2 vom Turm (gleiche Reihe), b1 vom König gedeckt, b2 (Turm) vom König
    # gedeckt (nicht schlagbar) - kein Zug, kein Schach.
    pos = Position(sq("c", 1), sq("b", 2), sq("a", 1), BLACK)
    assert not is_check(pos)
    assert legal_moves(pos) == []
    terminal, result = is_terminal(pos)
    assert terminal
    assert result == "patt"


def test_rook_captured_is_immediately_terminal_draw():
    pos = Position(sq("c", 1), None, sq("a", 1), WHITE)
    terminal, result = is_terminal(pos)
    assert terminal
    assert result == "turm_geschlagen"


def test_black_king_can_capture_undefended_rook():
    # WR direkt neben BK, WK weit weg -> Schwarz darf schlagen.
    pos = Position(sq("h", 8), sq("a", 2), sq("a", 1), BLACK)
    successors = legal_moves(pos)
    captured = [p for p in successors if p.white_rook is None]
    assert len(captured) == 1
    assert captured[0].black_king == sq("a", 2)


def test_black_king_cannot_capture_defended_rook():
    # WR neben BK, aber vom WK gedeckt -> Schlagen ist illegal.
    pos = Position(sq("b", 3), sq("a", 2), sq("a", 1), BLACK)
    successors = legal_moves(pos)
    captured = [p for p in successors if p.white_rook is None]
    assert captured == []


def test_rook_is_blocked_by_own_king():
    # Turm auf a1, weißer König auf a4 blockiert die a-Linie nach oben.
    pos = Position(sq("a", 4), sq("a", 1), sq("h", 8), WHITE)
    rook_moves = [p for p in legal_moves(pos) if p.white_king == sq("a", 4)]
    # Alle Zuege, bei denen der Koenig NICHT bewegt wurde, sind Turmzuege.
    targets = {p.white_rook for p in rook_moves}
    assert sq("a", 5) not in targets  # hinter dem eigenen Koenig blockiert
    assert sq("a", 3) in targets  # davor frei
    assert sq("a", 2) in targets


def test_white_king_cannot_move_onto_own_rook():
    pos = Position(sq("a", 1), sq("a", 2), sq("h", 8), WHITE)
    king_moves = [p for p in legal_moves(pos) if p.white_rook == sq("a", 2)]
    assert all(p.white_king != sq("a", 2) for p in king_moves)
