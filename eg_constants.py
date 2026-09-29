"""Feste Annahmen, Farben, Dateipfade."""

from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "eg_data" / "krk_tablebase.bin"

FILES = "abcdefgh"

LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#b58863"
HIGHLIGHT_SQUARE = "#7fb069"

# Gemessen (tools/build_tablebase.py, einmalig): siehe README/test_claims.py.
# Korrigiert (vom User gefunden): die Stellungsliste enthielt zunächst auch
# Stellungen, in denen die Seite, die NICHT am Zug ist, bereits im Schach
# steht (unmöglich - deren letzter Zug wäre illegal gewesen). Nach dem Fix
# 399.112 statt zuvor 447.888 legale Stellungen - siehe README für Details.
TOTAL_POSITIONS = 399_112
TOTAL_WINS = 376_868
TOTAL_DRAWS = 22_244
MAX_DTM_PLIES = 50
