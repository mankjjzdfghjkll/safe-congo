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
        text="&#128712;",
        showarrow=False,
        x=0.5,
        y=0.64,
        xref="paper",
        yref="paper",
        font=dict(size=28, color="#0a5fab"),
    )
    fig.add_annotation(
        text=f"<b>{title}</b><br><span style='font-size:12px'>{message}</span>",
        showarrow=False,
        x=0.5,
        y=0.43,
        xref="paper",
        yref="paper",
        align="center",
        font=dict(size=14, color=font_color),
        bgcolor="rgba(247,251,255,0.96)",
        bordercolor="rgba(180,208,232,0.9)",
        borderwidth=1,
        borderpad=16,
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig = layout_builder(fig, title)
    fig.update_layout(height=300, margin=dict(l=18, r=18, t=72, b=18))
    return fig