"""Zweites, unabhängiges Orakel für die KRK-Tablebase (ergänzt test_dtm_reference.py).

Anderer Rechenweg als `eg_retrograde`/`test_dtm_reference`: Legalität per Pseudozug + "eigener
König danach angegriffen?" (statt vorberechneter Angriffsmengen), Lösung per VORWÄRTS-Iteration
"Matt in <= k Halbzügen" mit numpy über die Kindertabelle (statt Vorgängergraph/Sweep). Verglichen
werden die ausgelieferte Binärtabelle (alle Stellungen), die Mengen legaler Stellungen und die
Zugerzeugung (Stichprobe) sowie `best_moves` (Stichprobe).
"""

import random

import pytest

np = pytest.importorskip("numpy")

from eg_chess import BLACK, WHITE, Position, legal_moves  # noqa: E402
from eg_tablebase import _load_table, best_moves, lookup  # noqa: E402

INF = 10**6


def _adj(a, b):
    return a != b and max(abs(a % 8 - b % 8), abs(a // 8 - b // 8)) <= 1


def _clear_between(a, b, blockers):
    ax, ay, bx, by = a % 8, a // 8, b % 8, b // 8
    if ax == bx:
        lo, hi = sorted((ay, by))
        return not any(y * 8 + ax in blockers for y in range(lo + 1, hi))
    if ay == by:
        lo, hi = sorted((ax, bx))
        return not any(ay * 8 + x in blockers for x in range(lo + 1, hi))
    return False


def _rook_attacks(rook, target, wk, bk):
    if rook is None or rook == target:
        return False
    if rook % 8 != target % 8 and rook // 8 != target // 8:
        return False
    return _clear_between(rook, target, {wk, bk} - {target})


_NB = [[t for t in range(64) if _adj(s, t)] for s in range(64)]


def _legal(wk, r, bk, stm):
    if len({wk, r, bk}) < 3 or _adj(wk, bk):
        return False
    return not (stm == 0 and _rook_attacks(r, bk, wk, bk))


def _children(wk, r, bk, stm):
    out = []
    if stm == 0:
        for t in _NB[wk]:
            if t not in (r, bk) and not _adj(t, bk):
                out.append((t, r, bk))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, y = r % 8 + dx, r // 8 + dy
            while 0 <= x < 8 and 0 <= y < 8 and y * 8 + x not in (wk, bk):
                out.append((wk, y * 8 + x, bk))
                x, y = x + dx, y + dy
    else:
        for t in _NB[bk]:
            if t == wk or _adj(wk, t):
                continue
            nr = None if t == r else r
            if nr is not None and _rook_attacks(nr, t, wk, t):
                continue
            out.append((wk, nr, t))
    return out


def _idx(wk, r, bk, stm):
    return ((wk * 64 + r) * 64 + bk) * 2 + stm


@pytest.fixture(scope="module")
def oracle():
    pos, start, child, mate = [], [0], [], []
    for wk in range(64):
        for r in range(64):
            for bk in range(64):
                for stm in (0, 1):
                    if not _legal(wk, r, bk, stm):
                        continue
                    ch = _children(wk, r, bk, stm)
                    pos.append(_idx(wk, r, bk, stm))
                    child.extend(-1 if c[1] is None else _idx(c[0], c[1], c[2], 1 - stm) for c in ch)
                    start.append(len(child))
                    mate.append(stm == 1 and not ch and _rook_attacks(r, bk, wk, bk))
    pos, start, child, mate = map(np.array, (pos, start, child, mate))
    n = len(pos)
    where = np.full(64 * 64 * 64 * 2, -1, dtype=np.int64)
    where[pos] = np.arange(n)
    crow = np.where(child < 0, n, where[np.maximum(child, 0)])
    assert (crow >= 0).all()
    val = np.full(n + 1, INF, dtype=np.int64)
    val[:n][mate] = 0
    lens = np.diff(start)
    ids = np.nonzero(lens > 0)[0]
    starts = start[:-1][ids]
    white = pos[ids] % 2 == 0
    k = 0
    while True:
        k += 1
        cv = val[crow]
        mn = np.minimum.reduceat(cv, starts)
        mx = np.maximum.reduceat(cv, starts)
        new = np.where(white, mn == k - 1, mx == k - 1) & (val[ids] == INF)
        if not new.any():
            break
        val[ids[new]] = k
    return pos, val[:n], int(mate.sum())


def _decode(p):
    return p // 8192, (p // 128) % 64, (p // 2) % 64, p % 2


def test_counts_and_table_equal_forward_oracle(oracle):
    pos, val, mates = oracle
    assert len(pos) == 399_112
    assert mates == 216
    assert int((val < INF).sum()) == 376_868
    assert int(val[val < INF].max()) == 32
    table = np.frombuffer(_load_table().tobytes(), dtype=np.uint16).astype(np.int64)
    expected = np.zeros(len(table), dtype=np.int64)
    expected[pos] = np.where(val < INF, val + 1, 0)
    assert np.array_equal(table, expected)


def test_move_generation_and_best_moves_match_oracle(oracle):
    pos, val, _ = oracle
    rng = random.Random(5)
    for i in rng.sample(range(len(pos)), 1500):
        wk, r, bk, stm = _decode(int(pos[i]))
        position = Position(wk, r, bk, WHITE if stm == 0 else BLACK)
        ch = _children(wk, r, bk, stm)
        got = sorted((c.white_king, -1 if c.white_rook is None else c.white_rook, c.black_king) for c in legal_moves(position))
        assert got == sorted((c[0], -1 if c[1] is None else c[1], c[2]) for c in ch)
        if not ch:
            continue

        def v(c):
            if c[1] is None:
                return INF
            return int(val[np.searchsorted(pos, _idx(c[0], c[1], c[2], 1 - stm))])

        vs = [v(c) for c in ch]
        if stm == 0:
            exp = {c for c, x in zip(ch, vs) if x == min(vs)}
        else:
            draws = {c for c, x in zip(ch, vs) if x >= INF}
            exp = draws or {c for c, x in zip(ch, vs) if x == max(vs)}
        assert {(c.white_king, c.white_rook, c.black_king) for c in best_moves(position)} == exp
        out = lookup(position)
        assert (out.result == "win") == (val[i] < INF)
        if val[i] < INF:
            assert out.dtm == val[i]
