"""Retrograde-Analyse: exakter Matt-Abstand (DTM) für JEDE legale
König+Turm-gegen-König-Stellung.

Implementiert ebenenweise (Sweep k setzt alle Stellungen mit DTM = k, bis
keine neue Ebene mehr entsteht) statt als klassische
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

    # Ebene für Ebene (Breitensuche rückwärts ab den Matt-Stellungen): Ebene k
    # enthält genau die Stellungen mit DTM = k. Eine Weiß-Stellung hat DTM k,
    # sobald ein Kind DTM k-1 hat (kein Kind mit kleinerem DTM, sonst wäre sie
    # schon in einer früheren Ebene gelöst); eine Schwarz-Stellung, sobald ALLE
    # Kinder Weiß-Siege sind und das größte Kind-DTM k-1 beträgt. Ein Sweep
    # liest nur den Stand bis Ebene k-1 (kein In-place-Update innerhalb einer
    # Ebene) - sonst bekäme eine Stellung schon in derselben Runde einen
    # zu großen DTM, der nie mehr korrigiert wird.
    level = 0
    while unresolved:
        level += 1
        solved_now: list[tuple[Position, int]] = []
        still_unresolved = []
        for pos in unresolved:
            children = children_cache[pos]
            if pos.side_to_move == WHITE:
                if any((co := outcome.get(c)) is not None and co.result == WIN and co.dtm == level - 1 for c in children):
                    solved_now.append((pos, level))
                    continue
            else:  # BLACK am Zug: Weiß gewinnt nur, wenn ALLE Antworten Weiß-Siege sind
                dtms = []
                for c in children:
                    co = outcome.get(c)
                    if co is None or co.result != WIN:
                        break
                    dtms.append(co.dtm)
                else:
                    if dtms and max(dtms) == level - 1:
                        solved_now.append((pos, level))
                        continue
            still_unresolved.append(pos)
        if not solved_now:
            break
        for pos, dtm in solved_now:
            outcome[pos] = Outcome(WIN, dtm)
        unresolved = still_unresolved

    # Alles, was nach dem Fixpunkt noch nicht klassifiziert ist, ist ein Remis
    # (Schwarz kann dem Matt für immer ausweichen).
    for pos in unresolved:
        outcome[pos] = Outcome(DRAW, None)

    return outcome
