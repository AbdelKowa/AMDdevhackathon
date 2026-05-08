"""Plotly figure builders for the dashboard.

Pure functions: take dicts in, return plotly figures. No Streamlit imports
so these are testable without a running app. Styled to sit on a dark
background — see .streamlit/config.toml for the matching app theme.
"""
from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

# Palette tuned for the dark theme in .streamlit/config.toml.
DEPOT_COLOR = "#FFD700"          # gold star — depot pops on dark
NODE_COLOR_OPEN = "#4FC3F7"      # cyan — open delivery node
NODE_COLOR_BLOCKED = "#ED1C24"   # AMD red — blocked / disrupted
ROUTE_COLORS = [
    "#FF8A65",  # warm orange
    "#BA68C8",  # violet
    "#81C784",  # green
    "#FFD54F",  # amber
    "#4DD0E1",  # teal
]
GRID_COLOR = "#2A2D34"
TEXT_COLOR = "#FAFAFA"


def build_grid_figure(
    world: dict[str, Any],
    routes: list[dict[str, Any]] | None = None,
    stage_label: str = "",
) -> go.Figure:
    """Render depot + delivery nodes + (optional) routes onto a 2D grid.

    Blocked nodes are AMD-red X markers, open nodes are cyan circles, depot
    is a gold star. Routes are drawn as colored polylines per vehicle.
    """
    fig = go.Figure()

    depot = world["depot"]
    nodes = world.get("nodes", [])
    open_nodes = [n for n in nodes if not n.get("blocked")]
    blocked_nodes = [n for n in nodes if n.get("blocked")]

    positions: dict[int, tuple[int, int]] = {depot["id"]: (depot["x"], depot["y"])}
    for n in nodes:
        positions[n["id"]] = (n["x"], n["y"])

    if routes:
        for i, route in enumerate(routes):
            stops = [s for s in route.get("stops", []) if s in positions]
            xs = [positions[s][0] for s in stops]
            ys = [positions[s][1] for s in stops]
            color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines+markers",
                    name=f"Vehicle {route.get('vehicle_id', i)}",
                    line=dict(color=color, width=3),
                    marker=dict(size=5, color=color),
                    hoverinfo="skip",
                )
            )

    if open_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in open_nodes],
                y=[n["y"] for n in open_nodes],
                mode="markers+text",
                marker=dict(
                    size=16,
                    color=NODE_COLOR_OPEN,
                    symbol="circle",
                    line=dict(color="#0E1117", width=2),
                ),
                text=[str(n["id"]) for n in open_nodes],
                textposition="top center",
                textfont=dict(color=TEXT_COLOR, size=11),
                name="Delivery node",
                hovertemplate="Node %{text}<extra></extra>",
            )
        )

    if blocked_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in blocked_nodes],
                y=[n["y"] for n in blocked_nodes],
                mode="markers+text",
                marker=dict(
                    size=18,
                    color=NODE_COLOR_BLOCKED,
                    symbol="x",
                    line=dict(color="#0E1117", width=2),
                ),
                text=[str(n["id"]) for n in blocked_nodes],
                textposition="top center",
                textfont=dict(color=NODE_COLOR_BLOCKED, size=11),
                name="Blocked",
                hovertemplate="Blocked node %{text}<extra></extra>",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[depot["x"]],
            y=[depot["y"]],
            mode="markers+text",
            marker=dict(
                size=24,
                color=DEPOT_COLOR,
                symbol="star",
                line=dict(color="#0E1117", width=2),
            ),
            text=["Depot"],
            textposition="bottom center",
            textfont=dict(color=DEPOT_COLOR, size=12),
            name="Depot",
            hovertemplate="Depot<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"Stage: {stage_label}" if stage_label else "Grid + routes",
            font=dict(size=16, color=TEXT_COLOR),
            x=0.01,
        ),
        xaxis=dict(
            title="x",
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            showspikes=False,
        ),
        yaxis=dict(
            title="y",
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            scaleanchor="x",
            scaleratio=1,
            showspikes=False,
        ),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color=TEXT_COLOR),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(26, 29, 36, 0.7)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
        ),
        height=540,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
