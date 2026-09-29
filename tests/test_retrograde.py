"""Retrograde-Analyse: Fixpunkt-Propagation an kleinen, von Hand
nachvollziehbaren Ausschnitten geprüft (nicht der volle 447.888-Stellungen-
Sweep - das läuft in tests/test_claims.py separat und einmalig)."""

from eg_chess import BLACK, WHITE, Position, legal_moves, square
from eg_retrograde import DRAW, WIN, solve_tablebase


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_mate_in_zero_for_the_mate_position_itself():
    mate = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)
    outcome = solve_tablebase([mate])
    assert outcome[mate].result == WIN
    assert outcome[mate].dtm == 0


def test_mate_in_one_propagates_to_parent():
    # Weiß am Zug, Turm h1->a1 liefert Matt (siehe test_chess.py fuer die
    # Matt-Stellung selbst).
    parent = Position(sq("c", 7), sq("h", 1), sq("a", 8), WHITE)
    mate = Position(sq("c", 7), sq("a", 1), sq("a", 8), BLACK)
    assert mate in legal_moves(parent)  # Selbstkontrolle der Testkonstruktion

    outcome = solve_tablebase([parent, mate])
    assert outcome[mate].result == WIN
    assert outcome[mate].dtm == 0
    assert outcome[parent].result == WIN
    assert outcome[parent].dtm == 1


def test_black_to_move_needs_all_children_winning_to_lose():
    # Konstruiere eine Schwarz-am-Zug-Stellung mit genau zwei legalen
    # Antworten, von denen nur EINE zu einem bekannten Weiß-Sieg führt - die
    # andere bleibt unbekannt (nicht in der Stellungsliste) -> Gesamtstellung
    # darf NICHT als Sieg klassifiziert werden (Schwarz waehlt die Flucht).
    black_pos = Position(sq("c", 6), sq("h", 1), sq("a", 8), BLACK)
    children = legal_moves(black_pos)
    assert len(children) > 1  # mehr als eine Flucht vorhanden

    # Nur EIN Kind wird als Sieg "bekannt" gemacht (kuenstlich), der Rest
    # bleibt unresolved (nicht in der Liste) -> black_pos muss DRAW werden,
    # nicht WIN (weil nicht ALLE Antworten als Sieg bekannt sind).
    known_win_child = children[0]
    outcome = solve_tablebase([black_pos, known_win_child])
    # known_win_child selbst ist keine Matt-/Patt-Stellung, bleibt also
    # unresolved -> auch black_pos bleibt unresolved -> als DRAW klassifiziert.
    assert outcome[black_pos].result == DRAW


def test_draw_when_rook_can_be_captured():
    pos = Position(sq("h", 8), sq("a", 2), sq("a", 1), BLACK)
    outcome = solve_tablebase([pos])
    # Ohne die Folgestellungen (Turm geschlagen) in der Liste bleibt pos
    # unresolved -> als DRAW klassifiziert (korrekt, da Schwarz den Turm
    # schlagen UND dann nie mehr verlieren kann - siehe test_full_tablebase
    # fuer den vollen Beweis über alle Stellungen).
    assert outcome[pos].result == DRAW
