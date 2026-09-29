"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code
nachgerechnet."""

import random

import pytest

import eg_constants as C
from eg_chess import WHITE, Position, is_legal_position
from eg_evaluation import heuristic_move
from eg_tablebase import best_moves, lookup


def test_readme_total_position_counts():
    # Unabhaengig bestaetigt: exakt 447.888 legale Stellungen ist eine
    # oeffentlich dokumentierte Tatsache ueber das KTK-Endspiel (Quelle im
    # README) - trifft hier exakt zu, ein starkes Signal fuer korrekte
    # Zug-/Legalitaetsregeln.
    assert C.TOTAL_POSITIONS == 447_888
    assert C.TOTAL_WINS + C.TOTAL_DRAWS == C.TOTAL_POSITIONS


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
    assert optimal == 466
    assert worsened == 1347
    assert allowed_draw == 187
