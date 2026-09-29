"""Endspiel-Tablebase: König+Turm gegen König, vollständig vorab gelöst per
Retrograde-Analyse (399.112 Stellungen, einmalig berechnet, siehe
tools/build_tablebase.py) - Vehikel-Wechsel zu einem echten Schach-Endspiel,
im Unterschied zum Mini-Vier-Gewinnt-Vehikel der übrigen Linie.

Kind-Stück von evaluation-function-demo (Adversarische-Suche-Linie).
"""

from __future__ import annotations

import streamlit as st

import eg_constants as C
from eg_chess import BLACK, WHITE, Position, is_terminal, legal_moves
from eg_evaluation import dtm_verdict, format_de_number, heuristic_move, move_destination
from eg_pdf_export import build_pdf
from eg_presets import (
    PRESET_HELP,
    PRESETS,
    apply_preset,
    init_session_state_defaults,
    load_permalink_settings,
    square_name,
    sync_query_params,
)
from eg_tablebase import best_moves, lookup
from eg_visualization import board_figure, dtm_histogram

_de = format_de_number

st.set_page_config(page_title="Endspiel-Tablebase – Sebastian Hanisch", layout="wide")

st.title("♟️ Endspiel-Tablebase: König+Turm gegen König, vollständig gelöst")
st.markdown(
    """
    **Vehikel-Wechsel:** statt Mini-Vier-Gewinnt diesmal ein echtes Schach-Endspiel – König und Turm gegen
    König, das klassische Beispiel für **Retrograde-Analyse** (Ken Thompsons erste vollständig berechnete
    Tablebase, 1986). Statt vorwärts zu suchen, wird **rückwärts von jeder Matt-/Patt-Stellung aus**
    propagiert, bis jede der 399.112 legalen Stellungen einen exakten Matt-Abstand hat – dieselbe
    Bellman-Rückwärtsrechnung wie in `value-iteration-demo` (Reinforcement-Learning-Linie), hier für ein
    Nullsummenspiel statt eines Erwartungswerts. Am Ende der Seite: die 📐 Mathematische Formulierung.
    """
)

st.caption("🎯 Schnellstart")
preset_cols = st.columns(len(PRESETS))
for col, name in zip(preset_cols, PRESETS):
    col.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])
st.caption("🔗 Die URL merkt sich die aktuelle Stellung (Permalink).")

load_permalink_settings()
init_session_state_defaults()

pos: Position = st.session_state["position"]
sync_query_params(pos)

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.caption(f"{C.TOTAL_POSITIONS:,} Stellungen vorab gelöst.".replace(",", "."))
    if st.button("↺ Zum Lehrbuch-Start zurück", use_container_width=True):
        apply_preset("Lehrbuch-Start (weit weg, Weiß gewinnt)")
        st.rerun()

terminal, result = is_terminal(pos)
outcome = lookup(pos)

st.subheader("Stellung")
board_col, info_col = st.columns([2, 1])

with board_col:
    optimal_targets = {move_destination(pos, m) for m in (best_moves(pos) if not terminal else [])}
    fig = board_figure(pos.white_king, pos.white_rook, pos.black_king, optimal_targets)
    st.plotly_chart(fig, use_container_width=False, key="board_chart")

with info_col:
    if terminal:
        if result == "matt":
            st.success("Matt! Weiß hat gewonnen.")
        elif result == "patt":
            st.info("Patt - Remis.")
        else:
            st.info("Turm geschlagen - totes Remis (nur noch zwei Könige).")
    else:
        st.metric("Am Zug", "Weiß" if pos.side_to_move == WHITE else "Schwarz")
        if outcome.result == "win":
            st.metric("Exakter Matt-Abstand", f"{outcome.dtm} Halbzüge")
        else:
            st.metric("Exaktes Ergebnis", "Remis")
        st.info(dtm_verdict(pos))

        h_move = heuristic_move(pos)
        h_is_optimal = h_move in best_moves(pos)
        st.caption(
            ("✅ " if h_is_optimal else "⚠️ ")
            + "Naive Faustregel (Königsabstand verkleinern) "
            + ("wählt hier ebenfalls optimal." if h_is_optimal else "würde hier NICHT optimal spielen (siehe Experiment unten).")
        )

        pdf_bytes = build_pdf(pos)
        st.download_button("📄 Analyse als PDF", data=pdf_bytes, file_name="tablebase_analyse.pdf", mime="application/pdf")

if not terminal:
    st.markdown("**Zug wählen:**")
    children = legal_moves(pos)
    optimal_set = set(best_moves(pos))

    def _describe(child: Position) -> str:
        dest = move_destination(pos, child)
        if pos.side_to_move == WHITE:
            if dest == child.white_king:
                moved = f"König {square_name(pos.white_king)}→{square_name(dest)}"
            else:
                moved = f"Turm {square_name(pos.white_rook)}→{square_name(dest)}"
        else:
            captured = " (Turm geschlagen!)" if child.white_rook is None else ""
            moved = f"König {square_name(pos.black_king)}→{square_name(dest)}{captured}"
        star = " ★" if child in optimal_set else ""
        return moved + star

    options = {_describe(c): c for c in children}
    choice = st.selectbox("Legale Züge (★ = optimal laut Tablebase)", options=list(options.keys()), key="move_select")
    if st.button("Zug ausführen", type="primary"):
        st.session_state["position"] = options[choice]
        st.session_state.pop("move_select", None)
        st.rerun()

st.markdown("---")
st.subheader("🔬 Wie gut ist eine einfache Faustregel wirklich?")
st.markdown(
    """
    Eine naheliegende Heuristik: **den eigenen König an den gegnerischen heranführen** (Königsabstand
    minimieren), den Turm dabei ignorieren. Gemessen an 2.000 zufälligen Gewinnstellungen für Weiß
    (`tests/test_claims.py`):
    """
)
st.plotly_chart(
    {
        "data": [
            {
                "type": "bar",
                "x": ["Optimal (schnellstes Matt)", "Gewinnt noch, aber langsamer", "Verschenkt den Sieg (Remis!)"],
                "y": [487, 1394, 119],
                "marker": {"color": ["#2ca02c", "#ff7f0e", "#d62728"]},
                "text": ["24,4 %", "69,7 %", "6,0 %"],
                "textposition": "outside",
            }
        ],
        "layout": {"height": 380, "margin": {"l": 10, "r": 10, "t": 20, "b": 10}, "yaxis": {"title": "Stellungen (von 2.000)", "fixedrange": True}, "xaxis": {"fixedrange": True}},
    },
    use_container_width=True,
    key="heuristic_chart",
)
st.warning(
    "**Ehrlicher Befund:** die Faustregel findet den schnellsten Weg nur in 24,4 % der Fälle - "
    "und in 6,0 % der Fälle verschenkt sie den bewiesenen Sieg komplett (der Zug führt in eine "
    "Remis-Stellung, weil der Turm dabei seine Kontrolle verliert). Königsabstand allein ist keine "
    "verlässliche Heuristik für dieses Endspiel - der Turm muss aktiv mitgedacht werden."
)

st.subheader("🔬 Wie verteilen sich die Matt-Abstände?")


@st.cache_data(show_spinner=False)
def _dtm_histogram():
    import array

    table = array.array("H")
    with open(C.DATA_PATH, "rb") as f:
        table.frombytes(f.read())
    hist: dict[int, int] = {}
    for raw in table:
        if raw > 0:
            hist[raw - 1] = hist.get(raw - 1, 0) + 1
    return hist


hist = _dtm_histogram()
st.plotly_chart(dtm_histogram(hist), use_container_width=True, key="dtm_hist_chart")
st.info(
    f"Von {_de(C.TOTAL_POSITIONS)} legalen Stellungen sind {_de(C.TOTAL_WINS)} ({C.TOTAL_WINS / C.TOTAL_POSITIONS:.1%}) "
    f"ein bewiesener Sieg für Weiß, {_de(C.TOTAL_DRAWS)} ({C.TOTAL_DRAWS / C.TOTAL_POSITIONS:.1%}) ein Remis. "
    f"Der längste erzwungene Weg zum Matt: {C.MAX_DTM_PLIES} Halbzüge."
)

st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
    - **Nur dieses eine Endspiel.** König+Turm gegen König hat genau 3 Figuren - eine vollständige
      Schach-Tablebase (mit Bauern, mehr Figuren) ist um viele Größenordnungen größer; die realen
      7-Steine-Tablebases brauchen Terabytes, nicht 1 MB.
    - **Die Heuristik oben ist bewusst naiv.** Reale Schachprogramme nutzen deutlich bessere KRK-Faustregeln
      (z. B. das Feld des schwarzen Königs mit dem Turm systematisch verkleinern) - hier bewusst ein
      einfaches, leicht widerlegbares Beispiel gewählt.
    - **Die Tablebase liegt vollständig im Arbeitsspeicher** (1 MB) - bei mehr Figuren wäre das nicht mehr
      möglich, echte Tablebases werden von der Festplatte nachgeladen.
    """
)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
        Retrograde-Analyse als Fixpunkt-Iteration (siehe `eg_retrograde.py`): für jede Stellung $s$ mit
        Nachfolgern $s' \in \text{Züge}(s)$,

        $$
        \text{DTM}(s) =
        \begin{cases}
        0 & s \text{ ist Matt} \\
        1 + \min_{s'} \text{DTM}(s') & \text{Weiß am Zug, mindestens ein } s' \text{ ist Sieg} \\
        1 + \max_{s'} \text{DTM}(s') & \text{Schwarz am Zug, ALLE } s' \text{ sind Sieg für Weiß} \\
        \text{Remis} & \text{sonst (Patt, Turm geschlagen, oder Schwarz kann ausweichen)}
        \end{cases}
        $$

        Strukturell identisch zur Bellman-Gleichung aus `value-iteration-demo` (dort Erwartungswert über
        stochastische Übergänge statt Minimax über einen Gegner) und zur Kürzeste-Wege-Bellman-Ford-DP
        (dort eine additive Kostenfunktion statt eines Sieg/Verlust-Werts). Auch verwandt mit
        Pattern-Database-Heuristiken in der Heuristischen-Baumsuche/A*-Linie: eine kleine, vorab exakt
        gelöste Teilproblem-Tabelle liefert eine zulässige Heuristik für größere Suchen (klassisch:
        15-Puzzle-Pattern-Databases).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
