"""PDF-Export der aktuellen Stellungs-Analyse (fpdf2).

`multi_cell(w=0, ...)` lässt den Cursor per Default am RECHTEN statt am linken
Rand stehen - ohne `new_x=LMARGIN` würde ein zweiter `multi_cell`-Aufruf direkt
danach abstürzen (bekannter Bug aus minimax-demo). Keine Sonderzeichen wie
„…" in PDF-gebundenen Strings (bekannter Bug aus alpha-beta-demo).
"""

from __future__ import annotations

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from eg_chess import WHITE, Position
from eg_evaluation import dtm_verdict
from eg_presets import square_name

_NEXT_LINE = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(pos: Position) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Endspiel-Tablebase - Analyse der aktuellen Stellung", **_NEXT_LINE)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Weißer König: {square_name(pos.white_king)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Weißer Turm: {square_name(pos.white_rook)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Schwarzer König: {square_name(pos.black_king)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Am Zug: {'Weiß' if pos.side_to_move == WHITE else 'Schwarz'}", **_NEXT_LINE)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Exaktes Ergebnis (Tablebase)", **_NEXT_LINE)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, dtm_verdict(pos), **_NEXT_LINE)

    return bytes(pdf.output())
