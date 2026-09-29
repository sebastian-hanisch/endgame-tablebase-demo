"""Löst die vollständige König+Turm-gegen-König-Tablebase EINMAL und schreibt
sie kompakt in eine Binärdatei (statt sie bei jedem App-Start 24-25s live neu
zu berechnen - echte Tablebases sind selbst vorab berechnete Dateien, kein
Live-Suchergebnis).

Kodierung je Stellung (Turm auf dem Brett - Stellungen ohne Turm sind immer
Remis und werden nicht gespeichert): Index
`((wk*64 + wr)*64 + bk)*2 + (0 wenn Weiß am Zug sonst 1)`, Wert als
unsigned short: 0 = Remis, sonst (Halbzüge bis Matt) + 1.
"""

import array
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eg_chess import WHITE  # noqa: E402
from eg_retrograde import DRAW, all_legal_positions, solve_tablebase  # noqa: E402

OUT_PATH = Path(__file__).resolve().parent.parent / "eg_data" / "krk_tablebase.bin"


def encode_index(wk: int, wr: int, bk: int, side_to_move: int) -> int:
    return ((wk * 64 + wr) * 64 + bk) * 2 + (0 if side_to_move == WHITE else 1)


def main() -> None:
    t0 = time.perf_counter()
    positions = all_legal_positions()
    print(f"{len(positions):,} legale Stellungen erzeugt ({time.perf_counter() - t0:.2f}s)")

    t0 = time.perf_counter()
    outcome = solve_tablebase(positions)
    print(f"gelöst in {time.perf_counter() - t0:.2f}s")

    wins = sum(1 for o in outcome.values() if o.result != DRAW)
    print(f"Siege: {wins:,}, Remis: {len(outcome) - wins:,}")

    table = array.array("H", [0]) * (64 * 64 * 64 * 2)
    for pos, out in outcome.items():
        idx = encode_index(pos.white_king, pos.white_rook, pos.black_king, pos.side_to_move)
        table[idx] = 0 if out.result == DRAW else (out.dtm + 1)

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        table.tofile(f)
    print(f"geschrieben: {OUT_PATH} ({OUT_PATH.stat().st_size:,} Bytes)")


if __name__ == "__main__":
    main()
