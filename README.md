# Endspiel-Tablebase: König+Turm gegen König, vollständig gelöst

Kind-Stück von **[evaluation-function-demo](https://github.com/sebastian-hanisch/evaluation-function-demo)**
(Adversarische-Suche-Linie). **Vehikel-Wechsel**: statt Mini-Vier-Gewinnt diesmal ein echtes
Schach-Endspiel – König und Turm gegen König (KTK), das klassische Beispiel für **Retrograde-Analyse**
(Ken Thompsons erste vollständig berechnete Schach-Tablebase, 1986).

## Warum dieses Problem

Bisher hat diese Linie immer VORWÄRTS gesucht (Minimax, Alpha-Beta, Bewertungsfunktion). Retrograde-Analyse
dreht das um: ausgehend von jeder Matt-/Patt-Stellung wird der Wert **rückwärts** propagiert, bis jede
erreichbare Stellung einen exakten Matt-Abstand (DTM, „distance to mate") hat. Für ein Endspiel mit nur
3 Figuren ist das vollständig durchführbar – 447.888 legale Stellungen, einmalig gelöst, danach nur noch
Tabellen-Nachschlag.

## Modell

Eigene, auf dieses Endspiel zugeschnittene Schachregeln (`eg_chess.py`) – kein allgemeiner Schach-Engine.
Felder als Ganzzahlen 0–63. Weiß (König+Turm) versucht Matt zu setzen, Schwarz (nur König) versucht zu
überleben (Patt oder den Turm schlagen).

## Methodik

Retrograde-Analyse als **Fixpunkt-Iteration** (`eg_retrograde.py`, wiederholte Sweeps bis keine Änderung
mehr eintritt) statt als klassische Vorgänger-Graph-Suche (die schnellere Variante echter
Tablebase-Generatoren) – strukturell identisch zur Bellman-Rückwärtsrechnung aus `value-iteration-demo`
(Reinforcement-Learning-Linie). Das Ergebnis wird einmalig berechnet und als kompakte Binärdatei
(`eg_data/krk_tablebase.bin`, 1 MB, `tools/build_tablebase.py`) mitgeliefert – die App löst nichts live,
sondern schlägt nach, wie eine echte Tablebase.

## Befunde (gemessen, keine Behauptungen)

- **447.888 legale Stellungen** – exakt die Zahl, die auch öffentlich für das KTK-Endspiel dokumentiert ist
  (siehe Quellen unten) – ein starkes externes Signal, dass die Zug-/Legalitätsregeln korrekt sind, ähnlich
  der Berger-Tafeln oder bbpPairings in der Turnierplanung-Linie.
- **425.644 Siege (95,0 %) für Weiß, 22.244 Remis (5,0 %).** Längster erzwungener Weg zum Matt: 50
  Halbzüge (25 Züge) – nahe am öffentlich dokumentierten Rekord von 26 Zügen für dieses Endspiel.
- **Eine naive Heuristik ("König heranführen, Turm ignorieren") wählt nur in 23,3 % der Fälle den
  schnellsten Weg zum Matt** (gemessen an 2.000 zufälligen Gewinnstellungen). In 67,4 % der Fälle gewinnt
  sie noch, aber langsamer. **In 9,4 % der Fälle verschenkt sie den bewiesenen Sieg komplett** (der Zug
  führt in eine Remis-Stellung) – Königsabstand allein ist keine verlässliche Faustregel, der Turm muss
  aktiv mitgedacht werden.

## Ehrliche Grenzen

- **Nur dieses eine Endspiel.** Eine vollständige Schach-Tablebase (mit Bauern, mehr Figuren) ist um viele
  Größenordnungen größer – echte 7-Steine-Tablebases brauchen Terabytes.
- **Die Heuristik ist bewusst naiv**, um einen klaren Kontrast zu zeigen – reale KRK-Engines nutzen
  bessere Faustregeln (z. B. das Feld des schwarzen Königs systematisch verkleinern).
- **Kein öffentlicher Referenzlöser zum direkten Abgleich jeder Einzelstellung verfügbar** – Korrektheit
  über zwei unabhängige Wege abgesichert: von Hand nachgerechnete Matt-/Patt-Beispiele
  (`tests/test_chess.py`) UND die exakte Übereinstimmung der Gesamt-Stellungszahl mit öffentlich
  dokumentierten Werten.

## Tests

46 Tests (`pytest tests/ -v`): Schachregeln (von Hand nachgerechnete Matt-/Patt-Stellungen, Turm-Fesselung,
Deckung), Retrograde-Analyse (Fixpunkt-Propagation an kleinen Ausschnitten), Tablebase-Nachschlag,
Heuristik, PDF-Export, Visualisierung, Streamlit-Rauchtests.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `eg_constants.py` | Farben, Pfade, gemessene Referenzwerte |
| `eg_chess.py` | König+Turm-gegen-König-Regeln |
| `eg_retrograde.py` | Retrograde-Analyse (Fixpunkt-Iteration) |
| `eg_tablebase.py` | Lädt/schlägt die vorberechnete Tablebase nach |
| `eg_evaluation.py` | Naive Heuristik, Verdikt-Texte |
| `eg_visualization.py` | Plotly-Schachbrett und Diagramme |
| `eg_presets.py` | Presets, Permalink, Session-Defaults |
| `eg_pdf_export.py` | PDF-Export |
| `tools/build_tablebase.py` | Löst die Tablebase einmalig, schreibt `eg_data/krk_tablebase.bin` |

## Bewusst nicht umgesetzt

- Vorgänger-Graph-basierte Retrograde-Analyse (die schnellere Variante echter Tablebase-Generatoren) –
  hier bewusst die langsamere, aber einfacher zu verifizierende Fixpunkt-Iteration.
- Weitere Endspiele (KQK, KPK, ...) – bewusst bei einem einzigen, klassischen Beispiel geblieben.

## Quellen

- [Endgame tablebase – Wikipedia](https://en.wikipedia.org/wiki/Endgame_tablebase)
- [The Endgames KRK and KQK](https://sites.google.com/site/jmptidcott2/KRK-KQK) (447.888 legale Stellungen,
  längstes Matt 26 Züge)

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.
