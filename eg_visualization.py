"""Plotly-Schachbrett (autorange statt expliziter range, siehe minimax-demo:
scaleanchor+range friert den Bereich anhand der Containerbreite ein)."""

from __future__ import annotations

import plotly.graph_objects as go

from eg_chess import file_of, rank_of
from eg_constants import DARK_SQUARE, FILES, HIGHLIGHT_SQUARE, LIGHT_SQUARE, PIECE_SYMBOLS


def board_figure(white_king: int, white_rook: int | None, black_king: int, highlight_squares: set[int] | None = None) -> go.Figure:
    highlight_squares = highlight_squares or set()
    fig = go.Figure()

    xs, ys, colours = [], [], []
    for r in range(8):
        for f in range(8):
            xs.append(f)
            ys.append(r)
            sq = r * 8 + f
            if sq in highlight_squares:
                colours.append(HIGHLIGHT_SQUARE)
            else:
                colours.append(LIGHT_SQUARE if (f + r) % 2 == 0 else DARK_SQUARE)

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker=dict(size=46, symbol="square", color=colours, line=dict(width=0)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    pieces = [("white_king", white_king), ("black_king", black_king)]
    if white_rook is not None:
        pieces.append(("white_rook", white_rook))
    fig.add_trace(
        go.Scatter(
            x=[file_of(sq) for _, sq in pieces],
            y=[rank_of(sq) for _, sq in pieces],
            mode="text",
            text=[PIECE_SYMBOLS[name] for name, _ in pieces],
            textfont=dict(size=34),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[-0.7, 7.7],
            y=[-0.7, 7.7],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_xaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickmode="array",
        tickvals=list(range(8)),
        ticktext=list(FILES),
        fixedrange=True,
    )
    fig.update_yaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickmode="array",
        tickvals=list(range(8)),
        ticktext=[str(r + 1) for r in range(8)],
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1,
    )
    fig.update_layout(height=560, width=560, margin=dict(l=30, r=10, t=10, b=30), plot_bgcolor="white")
    return fig


def dtm_histogram(histogram: dict[int, int]) -> go.Figure:
    dtms = sorted(histogram.keys())
    counts = [histogram[d] for d in dtms]
    fig = go.Figure(go.Bar(x=dtms, y=counts, marker_color="#6a4c93"))
    fig.update_xaxes(title="Matt-Abstand (Halbzüge)", fixedrange=True)
    fig.update_yaxes(title="Anzahl Stellungen", fixedrange=True)
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
    return fig
