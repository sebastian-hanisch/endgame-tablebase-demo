"""Retrograde-Analyse: exakter Matt-Abstand (DTM) für JEDE legale
König+Turm-gegen-König-Stellung.

Implementiert als Fixpunkt-Iteration (wiederholte Sweeps über alle
Stellungen, bis sich nichts mehr ändert) statt als klassische
Vorgänger-Graph-Suche (die Variante echter Tablebase-Generatoren, z. B. Ken
Thompson 1986) - langsamer, aber strukturell identisch zur
Bellman-Rückwärtsrechnung aus value-iteration-demo (Reinforcement-Learning-
Linie): Werte terminaler Zustände (hier: Matt/Patt) werden rückwärts
propagiert, bis der Fixpunkt (alle erreichbaren Werte bekannt) erreicht ist.

Wert einer Stellung: "win" (Weiß erzwingt Matt, mit Zügen bis dahin) oder
"draw" (Schwarz kann Matt für immer vermeiden - Patt, Turm schlagen, oder
ewiges Ausweichen).
"""

from __future__ import annotations

from dataclasses import dataclass

from eg_chess import BLACK, WHITE, Position, is_legal_position, is_terminal, legal_moves

WIN = "win"
DRAW = "draw"


@dataclass(frozen=True)
class Outcome:
    result: str  # WIN oder DRAW
    dtm: int | None  # Halbzüge bis zum Matt (None bei DRAW)


def all_legal_positions(with_rook_only: bool = True) -> list[Position]:
    positions = []
    for wk in range(64):
        for wr in range(64):
            if wr == wk:
                continue
            for bk in range(64):
                if bk in (wk, wr):
                    continue
                for stm in (WHITE, BLACK):
                    pos = Position(wk, wr, bk, stm)
                    if is_legal_position(pos):
                        positions.append(pos)
    return positions


def solve_tablebase(positions: list[Position] | None = None) -> dict[Position, Outcome]:
    """Löst ALLE übergebenen (oder aller legalen) Stellungen exakt."""
    if positions is None:
        positions = all_legal_positions()

    outcome: dict[Position, Outcome] = {}
    children_cache: dict[Position, list[Position]] = {}
    unresolved: list[Position] = []

    for pos in positions:
        terminal, result = is_terminal(pos)
        if terminal:
            if result == "matt":
                outcome[pos] = Outcome(WIN, 0)
            else:
                outcome[pos] = Outcome(DRAW, None)
        else:
            children_cache[pos] = legal_moves(pos)
            unresolved.append(pos)

    changed = True
    while changed:
        changed = False
        still_unresolved = []
        for pos in unresolved:
            children = children_cache[pos]
            if pos.side_to_move == WHITE:
                best = None
                for c in children:
                    co = outcome.get(c)
                    if co is not None and co.result == WIN:
                        if best is None or co.dtm < best:
                            best = co.dtm
                if best is not None:
                    outcome[pos] = Outcome(WIN, best + 1)
                    changed = True
                    continue
            else:  # BLACK am Zug: Weiß gewinnt nur, wenn ALLE Antworten Weiß-Siege sind
                dtms = []
                all_win = True
                for c in children:
                    co = outcome.get(c)
                    if co is None or co.result != WIN:
                        all_win = False
                        break
                    dtms.append(co.dtm)
                if all_win and dtms:
                    outcome[pos] = Outcome(WIN, max(dtms) + 1)
                    changed = True
                    continue
            still_unresolved.append(pos)
        unresolved = still_unresolved

    # Alles, was nach dem Fixpunkt noch nicht klassifiziert ist, ist ein Remis
    # (Schwarz kann dem Matt für immer ausweichen).
    for pos in unresolved:
        outcome[pos] = Outcome(DRAW, None)

    return outcome
