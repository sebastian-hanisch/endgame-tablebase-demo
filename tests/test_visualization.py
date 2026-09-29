"""Regressionstest gegen den in minimax-demo gefundenen scaleanchor+range-Bug."""

from eg_chess import square
from eg_visualization import board_figure, dtm_histogram


def sq(file_letter: str, rank_number: int) -> int:
    return square(ord(file_letter) - ord("a"), rank_number - 1)


def test_board_figure_uses_autorange_not_explicit_range():
    fig = board_figure(sq("a", 1), sq("h", 1), sq("h", 8))
    assert fig.layout.xaxis.autorange is True
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.autorange is True
    assert fig.layout.yaxis.range is None


def test_board_figure_has_64_squares():
    fig = board_figure(sq("a", 1), sq("h", 1), sq("h", 8))
    assert len(fig.data[0].x) == 64


def test_board_figure_without_rook_still_renders():
    fig = board_figure(sq("a", 1), None, sq("h", 8))
    text_trace = next(t for t in fig.data if t.mode == "text")
    assert len(text_trace.text) == 2  # nur die beiden Koenige


def test_board_figure_with_rook_has_three_pieces():
    fig = board_figure(sq("a", 1), sq("d", 4), sq("h", 8))
    text_trace = next(t for t in fig.data if t.mode == "text")
    assert len(text_trace.text) == 3
    marker_trace = next(t for t in fig.data if t.mode == "markers" and len(t.x) == 3)
    assert list(marker_trace.marker.color) == ["#f7f3e8", "#2b2b2b", "#f7f3e8"]  # weiss, schwarz, weiss


def test_dtm_histogram_has_one_bar_per_dtm_value():
    hist = {0: 5, 1: 3, 2: 7}
    fig = dtm_histogram(hist)
    assert len(fig.data[0].x) == 3
