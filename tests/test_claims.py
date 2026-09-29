"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code
nachgerechnet."""

import random

import pytest

import eg_constants as C
from eg_chess import WHITE, Position, is_legal_position
from eg_evaluation import heuristic_move
from eg_tablebase import best_moves, lookup


def test_readme_total_position_counts():
    # Echter, vom User gefundener Bug: die Stellungsliste enthielt zunaechst
    # auch Stellungen, in denen die Seite, die NICHT am Zug ist, bereits im
    # Schach steht (unmoeglich - siehe eg_chess.is_legal_position). Nach dem
    # Fix 399.112 statt der zuvor faelschlich mit der oeffentlich
    # dokumentierten Zahl (447.888) uebereinstimmenden Menge - siehe README.
    assert C.TOTAL_POSITIONS == 399_112
    assert C.TOTAL_WINS + C.TOTAL_DRAWS == C.TOTAL_POSITIONS


def test_side_not_to_move_in_check_is_illegal():
    from eg_chess import square

    def sq(f, r):
        return square(ord(f) - ord("a"), r - 1)

    # Der urspruengliche (fehlerhafte) "Lehrbuch-Start"-Preset: Schwarz auf
    # h8 stand im Schach vom Turm auf h1, obwohl Weiss am Zug war - unmoeglich,
    # da Schwarz seinen letzten Zug dann illegal ins Schach gemacht haette.
    pos = Position(sq("a", 1), sq("h", 1), sq("h", 8), WHITE)
    assert not is_legal_position(pos)


def test_legal_positions_children_are_always_legal():
    # Bestaetigt, dass der Fix rein SUBTRAKTIV ist: kein legaler Zug aus einer
    # legalen Stellung fuehrt je in eine (jetzt ausgeschlossene) illegale
    # Stellung - die exakten Werte aller weiterhin legalen Stellungen aendern
    # sich durch den Fix also nicht (siehe README).
    from eg_chess import legal_moves

    rng = random.Random(3)
    checked = 0
    for _ in range(500):
        wk, wr, bk = rng.randrange(64), rng.randrange(64), rng.randrange(64)
        if len({wk, wr, bk}) < 3:
            continue
        pos = Position(wk, wr, bk, WHITE)
        if not is_legal_position(pos):
            continue
        for child in legal_moves(pos):
            checked += 1
            assert is_legal_position(child)
    assert checked > 1000


def test_readme_heuristic_agreement_rate():
    rng = random.Random(7)
    sample = []
    while len(sample) < 2000:
        wk, wr, bk = rng.randrange(64), rng.randrange(64), rng.randrange(64)
        if len({wk, wr, bk}) < 3:
            continue
        pos = Position(wk, wr, bk, WHITE)
        if not is_legal_position(pos):
            continue
        if lookup(pos).result != "win":
            continue
        sample.append(pos)

    optimal = worsened = allowed_draw = 0
    for pos in sample:
        h_move = heuristic_move(pos)
        bm = best_moves(pos)
        if h_move in bm:
            optimal += 1
        else:
            h_out = lookup(h_move)
            if h_out.result == "draw":
                allowed_draw += 1
            else:
                worsened += 1

    assert len(sample) == 2000
    assert optimal == 487
    assert worsened == 1394
    assert allowed_draw == 119
