"""Regressionstest: aufeinanderfolgende multi_cell-Aufrufe dürfen nicht
crashen, keine fpdf2-Crash-Zeichen in PDF-gebundenen Strings."""

from eg_chess import BLACK, WHITE, Position, square
from eg_pdf_export import build_pdf


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_build_pdf_does_not_crash():
    pos = Position(sq("c", 7), sq("h", 1), sq("a", 8), WHITE)
    pdf_bytes = build_pdf(pos)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_build_pdf_for_draw_does_not_crash():
    pos = Position(sq("c", 1), sq("b", 2), sq("a", 1), BLACK)
    pdf_bytes = build_pdf(pos)
    assert pdf_bytes.startswith(b"%PDF")
