"""Plotly figure builders for the dashboard.

Pure functions: take dicts in, return plotly figures. No Streamlit imports
so these are testable without a running app.
"""
from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

DEPOT_COLOR = "#2ca02c"
NODE_COLOR_OPEN = "#1f77b4"
NODE_COLOR_BLOCKED = "#d62728"
ROUTE_COLORS = ["#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#17becf"]


def build_grid_figure(
    world: dict[str, Any],
    routes: list[dict[str, Any]] | None = None,
    stage_label: str = "",
) -> go.Figure:
    """Render depot + delivery nodes + (optional) routes onto a 2D grid.

    Blocked nodes are red X markers, open nodes are blue circles, depot
    is a green star. Routes are drawn as colored polylines.
    """
    fig = go.Figure()

    depot = world["depot"]
    nodes = world.get("nodes", [])
    open_nodes = [n for n in nodes if not n.get("blocked")]
    blocked_nodes = [n for n in nodes if n.get("blocked")]

    # node_id -> (x, y) lookup for plotting routes
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
                    line=dict(color=color, width=2),
                    marker=dict(size=4, color=color),
                    hoverinfo="skip",
                )
            )

    if open_nodes:
        fig.add_trace(
            go.Scatter(
                x=[n["x"] for n in open_nodes],
                y=[n["y"] for n in open_nodes],
                mode="markers+text",
                marker=dict(size=14, color=NODE_COLOR_OPEN, symbol="circle"),
                text=[str(n["id"]) for n in open_nodes],
                textposition="top center",
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
                marker=dict(size=14, color=NODE_COLOR_BLOCKED, symbol="x"),
                text=[str(n["id"]) for n in blocked_nodes],
                textposition="top center",
                name="Blocked",
                hovertemplate="Blocked node %{text}<extra></extra>",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[depot["x"]],
            y=[depot["y"]],
            mode="markers+text",
            marker=dict(size=22, color=DEPOT_COLOR, symbol="star"),
            text=["Depot"],
            textposition="bottom center",
            name="Depot",
            hovertemplate="Depot<extra></extra>",
        )
    )

    title = f"Stage: {stage_label}" if stage_label else "Grid + routes"
    fig.update_layout(
        title=title,
        xaxis=dict(title="x"),
        yaxis=dict(title="y", scaleanchor="x", scaleratio=1),
        showlegend=True,
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
