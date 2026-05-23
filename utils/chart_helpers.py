from typing import Callable, Optional

import plotly.graph_objects as go


def empty_state_figure(
    title: str,
    message: str,
    layout_builder: Callable[[go.Figure, Optional[str]], go.Figure],
    font_color: str = "#6b7f99",
) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        showarrow=False,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        font=dict(size=14, color=font_color),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return layout_builder(fig, title)