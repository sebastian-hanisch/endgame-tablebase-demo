"""Regressionstest gegen einen UNABHÄNGIG geschriebenen KRK-Löser.

Früherer Fehler: `solve_tablebase` aktualisierte den Matt-Abstand (DTM) im
Sweep in-place (Gauß-Seidel) und überarbeitete ihn nie - die Gewinnmenge war
richtig, aber 305.220 von 376.868 DTM-Werte waren zu groß (Maximum 50 statt
32 Halbzüge). Diese Referenz nutzt eigene Regeln (x/y-Koordinaten statt
Feldnummern, eigene Zugerzeugung) und eine Vorgänger-Zähler-BFS ebenenweise
ab den Matt-Stellungen - sie teilt keinen Code mit eg_chess/eg_retrograde.
"""

import array

import pytest

import eg_constants as C
from eg_chess import WHITE, Position
from eg_retrograde import all_legal_positions, solve_tablebase

SQUARES = [(x, y) for y in range(8) for x in range(8)]


def _ok(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def _adj(a, b):
    return a != b and max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= 1


def _rook_attacks(rook, wk, bk, through_bk):
    att = set()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        x, y = rook
        while True:
            x, y = x + dx, y + dy
            if not _ok(x, y) or (x, y) == wk:
                break
            if (x, y) == bk and not through_bk:
                att.add((x, y))
                break
            att.add((x, y))
    return att


def _in_check(wk, rook, bk):
    return rook is not None and bk in _rook_attacks(rook, wk, bk, False)


def _moves(wk, rook, bk, stm):
    out = []
    if stm == 0:  # Weiß
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                t = (wk[0] + dx, wk[1] + dy)
                if (dx or dy) and _ok(*t) and t != rook and t != bk and not _adj(t, bk):
                    out.append((t, rook, bk, 1))
        if rook is not None:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x, y = rook
                while True:
                    x, y = x + dx, y + dy
                    if not _ok(x, y) or (x, y) in (wk, bk):
                        break
                    out.append((wk, (x, y), bk, 1))
    else:  # Schwarz
        att = _rook_attacks(rook, wk, bk, True) if rook is not None else set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                t = (bk[0] + dx, bk[1] + dy)
                if not (dx or dy) or not _ok(*t) or t == wk or _adj(t, wk):
                    continue
                if t == rook:
                    out.append((wk, None, t, 0))
                elif t not in att:
                    out.append((wk, rook, t, 0))
    return out


def _reference_dtm() -> dict:
    pos = []
    for wk in SQUARES:
        for r in SQUARES:
            if r == wk:
                continue
            for bk in SQUARES:
                if bk in (wk, r) or _adj(wk, bk):
                    continue
                pos.append((wk, r, bk, 1))
                if not _in_check(wk, r, bk):
                    pos.append((wk, r, bk, 0))
    children = {p: _moves(*p) for p in pos}
    preds = {p: [] for p in pos}
    for p, cs in children.items():
        for q in cs:
            if q[1] is not None:  # Stellungen ohne Turm sind immer Remis
                preds[q].append(p)
    dtm = {p: 0 for p in pos if p[3] == 1 and not children[p] and _in_check(p[0], p[1], p[2])}
    frontier = list(dtm)
    done_children: dict = {}
    level = 0
    while frontier:
        nxt = []
        for q in frontier:
            for p in preds[q]:
                if p in dtm:
                    continue
                if p[3] == 0:
                    dtm[p] = level + 1
                    nxt.append(p)
                else:
                    done_children[p] = done_children.get(p, 0) + 1
                    if done_children[p] == len(children[p]):
                        dtm[p] = level + 1
                        nxt.append(p)
        level += 1
        frontier = nxt
    return dtm


def _xy(sq):
    return (sq % 8, sq // 8)


@pytest.fixture(scope="module")
def reference():
    return _reference_dtm()


def test_reference_matches_published_counts_and_maximum(reference):
    assert len(reference) == C.TOTAL_WINS
    assert max(reference.values()) == C.MAX_DTM_PLIES == 32
    # Weiß am Zug: längstes Matt = 16 Züge (31 Halbzüge), der bekannte KRK-Wert.
    assert max(v for p, v in reference.items() if p[3] == 0) == 31


def test_shipped_tablebase_equals_independent_reference(reference):
    from eg_tablebase import _load_table

    table = _load_table()
    expected = array.array("H", [0]) * len(table)
    for (wk, r, bk, stm), v in reference.items():
        idx = (((wk[1] * 8 + wk[0]) * 64 + r[1] * 8 + r[0]) * 64 + bk[1] * 8 + bk[0]) * 2 + stm
        expected[idx] = v + 1
    assert table == expected


def test_solve_tablebase_equals_independent_reference(reference):
    outcome = solve_tablebase(all_legal_positions())
    wins = {p: o.dtm for p, o in outcome.items() if o.result == "win"}
    assert len(wins) == len(reference)
    for pos, dtm in wins.items():
        key = (_xy(pos.white_king), _xy(pos.white_rook), _xy(pos.black_king), 0 if pos.side_to_move == WHITE else 1)
        assert reference[key] == dtm
