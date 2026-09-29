"""Feste Annahmen, Farben, Dateipfade."""

from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "eg_data" / "krk_tablebase.bin"

FILES = "abcdefgh"

PIECE_SYMBOLS = {"white_king": "♔", "white_rook": "♖", "black_king": "♚"}

LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#b58863"
HIGHLIGHT_SQUARE = "#7fb069"

# Gemessen (tools/build_tablebase.py, einmalig): siehe README/test_claims.py.
TOTAL_POSITIONS = 447_888
TOTAL_WINS = 425_644
TOTAL_DRAWS = 22_244
MAX_DTM_PLIES = 50
