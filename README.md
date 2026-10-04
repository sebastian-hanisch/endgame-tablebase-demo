# Endspiel-Tablebase: König+Turm gegen König, vollständig gelöst

Kind-Stück von **[evaluation-function-demo](https://github.com/sebastian-hanisch/evaluation-function-demo)**
(Adversarische-Suche-Linie). **Vehikel-Wechsel**: statt Mini-Vier-Gewinnt diesmal ein echtes
Schach-Endspiel – König und Turm gegen König (KTK), das klassische Beispiel für **Retrograde-Analyse**
(Ken Thompsons erste vollständig berechnete Schach-Tablebase, 1986).

## Warum dieses Problem

Bisher hat diese Linie immer VORWÄRTS gesucht (Minimax, Alpha-Beta, Bewertungsfunktion). Retrograde-Analyse
dreht das um: ausgehend von jeder Matt-/Patt-Stellung wird der Wert **rückwärts** propagiert, bis jede
erreichbare Stellung einen exakten Matt-Abstand (DTM, „distance to mate") hat. Für ein Endspiel mit nur
3 Figuren ist das vollständig durchführbar – 399.112 legale Stellungen, einmalig gelöst, danach nur noch
Tabellen-Nachschlag.

## Modell

Eigene, auf dieses Endspiel zugeschnittene Schachregeln (`eg_chess.py`) – kein allgemeiner Schach-Engine.
Felder als Ganzzahlen 0–63. Weiß (König+Turm) versucht Matt zu setzen, Schwarz (nur König) versucht zu
überleben (Patt oder den Turm schlagen).

## Methodik

Retrograde-Analyse **ebenenweise** (`eg_retrograde.py`: Sweep *k* setzt alle Stellungen mit DTM = *k*,
bis keine neue Ebene mehr entsteht) statt als klassische Vorgänger-Graph-Suche (die schnellere Variante echter
Tablebase-Generatoren) – strukturell identisch zur Bellman-Rückwärtsrechnung aus `value-iteration-demo`
(Reinforcement-Learning-Linie). Das Ergebnis wird einmalig berechnet und als kompakte Binärdatei
(`eg_data/krk_tablebase.bin`, 1 MB, `tools/build_tablebase.py`) mitgeliefert – die App löst nichts live,
sondern schlägt nach, wie eine echte Tablebase.

## Befunde (gemessen, keine Behauptungen)

- **399.112 legale Stellungen, 376.868 Siege (94,4 %) für Weiß, 22.244 Remis (5,6 %).** Längster
  erzwungener Weg zum Matt: 32 Halbzüge (Schwarz am Zug); mit Weiß am Zug höchstens 31 Halbzüge, also
  Matt in 16 Zügen.
- **Eine naive Heuristik ("König heranführen, Turm ignorieren") wählt nur in 31,4 % der Fälle den
  schnellsten Weg zum Matt** (gemessen an 2.000 zufälligen Gewinnstellungen). In 62,7 % der Fälle gewinnt
  sie noch, aber langsamer. **In 6,0 % der Fälle verschenkt sie den bewiesenen Sieg komplett** (der Zug
  führt in eine Remis-Stellung) – Königsabstand allein ist keine verlässliche Faustregel, der Turm muss
  aktiv mitgedacht werden.

## Befunde und Korrekturen gegenüber dem Plan

Zwei echte, vom Nutzer gefundene Bugs nach dem ersten Deploy (plus ein dritter, bei einer späteren
Nachprüfung gefundener, siehe Punkt 3):

1. **Ungültige Stellungen zugelassen.** `is_legal_position` prüfte ursprünglich nur "Könige verschieden,
   Turm nicht auf einem Königsfeld, Könige nicht benachbart" – NICHT aber die Grundregel, dass die Seite,
   die NICHT am Zug ist, nicht bereits im Schach stehen darf (sie hätte ihren letzten Zug sonst illegal
   ins Schach hinein gemacht). Der ursprüngliche „Lehrbuch-Start"-Preset zeigte genau das: Schwarz im
   Schach vom Turm, obwohl Weiß am Zug war. Die (zunächst als externe Bestätigung gefeierte) exakte
   Übereinstimmung der Gesamt-Stellungszahl mit der öffentlich dokumentierten Zahl 447.888 war dadurch
   ein Zufallstreffer mit einer ANDEREN, loseren Zählkonvention – nach dem Fix sind es korrekt 399.112
   legale Stellungen. Wichtig: der Fix ist rein SUBTRAKTIV – jeder Zug aus einer weiterhin legalen
   Stellung führt nachweislich (`tests/test_claims.py::test_legal_positions_children_are_always_legal`)
   nie in eine der jetzt ausgeschlossenen Stellungen, die exakten Matt-Abstände aller echten Stellungen
   sind also unverändert richtig geblieben – nur die (vorher zu große) Gesamtzahl war falsch.
2. **Figuren auf dem Brett kaum zu erkennen.** Reine Unicode-Schachsymbole (♔♖♚) ohne Hintergrundfarbe und
   ohne Kontrastfarbe im Text unterschieden sich auf dem karierten Brett kaum. Fix: wie bei den
   Connect4-Demos dieser Linie eine farbige Kreisscheibe je Figur (klarer Weiß/Schwarz-Kontrast) mit
   einem fett beschrifteten Buchstaben (K/T) statt eines duennen Glyphs.
3. **Matt-Abstände (DTM) nicht minimal.** Die erste Fassung von `solve_tablebase` vergab die DTM im Sweep
   in-place (Gauß-Seidel) und überarbeitete sie nie: die Gewinn-/Remismenge (376.868 / 22.244) war
   richtig, aber 305.220 der 376.868 Matt-Abstände waren zu groß – angezeigt wurden bis zu 50 Halbzüge
   (25 Züge) statt der tatsächlichen 32 Halbzüge (Matt in 16 Zügen mit Weiß am Zug, der bekannte
   KRK-Wert). Behoben durch ebenenweise Retrograde-Analyse (Ebene *k* liest nur den Stand bis Ebene
   *k*−1); die Tabelle wurde neu erzeugt und stimmt in allen 399.112 Stellungen mit einer unabhängig
   geschriebenen Referenz überein (`tests/test_dtm_reference.py`). Dadurch änderten sich auch die
   Heuristik-Messwerte (optimal: 31,4 % statt 24,4 %, langsamer: 62,7 % statt 69,7 %; Sieg verschenkt
   unverändert 6,0 %) und der Lehrbuch-Start (Matt in 12 Zügen, 23 Halbzüge, statt 25 Halbzüge). Die
   Aussage in Punkt 1, die exakten Matt-Abstände seien durch den Stellungs-Fix unverändert geblieben,
   bezieht sich nur auf diesen Fix – die Werte selbst waren wegen Fehler 3 schon vorher zu groß.

## Ehrliche Grenzen

- **Nur dieses eine Endspiel.** Eine vollständige Schach-Tablebase (mit Bauern, mehr Figuren) ist um viele
  Größenordnungen größer – echte 7-Steine-Tablebases brauchen Terabytes.
- **Die Heuristik ist bewusst naiv**, um einen klaren Kontrast zu zeigen – reale KRK-Engines nutzen
  bessere Faustregeln (z. B. das Feld des schwarzen Königs systematisch verkleinern).
- **Kein öffentlicher Referenzlöser zum direkten Abgleich jeder Einzelstellung verfügbar** – Korrektheit
  über von Hand nachgerechnete Matt-/Patt-Beispiele abgesichert (`tests/test_chess.py`) und über eine
  unabhängig geschriebene Referenz (eigene Zugerzeugung, Vorgänger-Zähler statt Sweeps,
  `tests/test_dtm_reference.py`), die für alle 399.112 Stellungen exakt dieselben DTM-Werte liefert.

## Tests

53 Tests (`pytest tests/ -v`): Schachregeln (von Hand nachgerechnete Matt-/Patt-Stellungen, Turm-Fesselung,
Deckung), Retrograde-Analyse (Propagation an kleinen Ausschnitten, Abgleich aller DTM-Werte mit einer
unabhängigen Referenz), Tablebase-Nachschlag,
Heuristik, PDF-Export, Visualisierung, Streamlit-Rauchtests.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `eg_constants.py` | Farben, Pfade, gemessene Referenzwerte |
| `eg_chess.py` | König+Turm-gegen-König-Regeln |
| `eg_retrograde.py` | Retrograde-Analyse (ebenenweise) |
| `eg_tablebase.py` | Lädt/schlägt die vorberechnete Tablebase nach |
| `eg_evaluation.py` | Naive Heuristik, Verdikt-Texte |
| `eg_visualization.py` | Plotly-Schachbrett und Diagramme |
| `eg_presets.py` | Presets, Permalink, Session-Defaults |
| `eg_pdf_export.py` | PDF-Export |
| `tools/build_tablebase.py` | Löst die Tablebase einmalig, schreibt `eg_data/krk_tablebase.bin` |

## Bewusst nicht umgesetzt

- Vorgänger-Graph-basierte Retrograde-Analyse (die schnellere Variante echter Tablebase-Generatoren) –
  hier bewusst die langsamere, aber einfacher zu verifizierende ebenenweise Sweep-Suche.
- Weitere Endspiele (KQK, KPK, ...) – bewusst bei einem einzigen, klassischen Beispiel geblieben.

## Quellen

- [Endgame tablebase – Wikipedia](https://en.wikipedia.org/wiki/Endgame_tablebase)
- [The Endgames KRK and KQK](https://sites.google.com/site/jmptidcott2/KRK-KQK) (nennt 447.888 legale
  Stellungen und ein längstes Matt von 26 Zügen – die dortige Zählung schließt offenbar, anders als hier,
  Stellungen mit ein, in denen die nicht am Zug befindliche Seite bereits im Schach steht; unser
  unabhängig nachgerechnetes längstes Matt von 16 Zügen entspricht dem in der Literatur üblichen
  KRK-Wert, den 26-Züge-Wert dieser Quelle konnten wir nicht nachvollziehen)

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Adversarische Suche: Minimax bis Selbstspiel](https://sebastianhanisch.net/konzepte-adversarische-suche.html).
