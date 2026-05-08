"""Streamlit dashboard for the delivery-logistics demo.

Reads `output/last_run.json` (written by `python -m src.main`) and renders
the grid + routes + metrics. Click "Refresh" after a fresh main.py run.

Run with: `streamlit run dashboard/app.py`
"""
from __future__ import annotations

import sys
from pathlib import Path

# Streamlit invokes this file as a script (not as `dashboard.app`), so the
# project root isn't on sys.path and `from dashboard.* import ...` would
# fail. Insert the project root before anything else imports.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st  # noqa: E402  -- must come after sys.path shim above

from dashboard.charts import build_grid_figure  # noqa: E402
from dashboard.data import (  # noqa: E402
    DEFAULT_ARTIFACT_PATH,
    get_routes_for_stage,
    load_artifact,
    stages_with_routes,
)

st.set_page_config(page_title="Delivery Logistics Demo", layout="wide")
st.title("Delivery Logistics — agent-optimized routing")

artifact = load_artifact()
if artifact is None:
    st.warning(
        f"No artifact found at `{DEFAULT_ARTIFACT_PATH}`. Generate one with:\n\n"
        "```\npython -m src.main --placeholder\n```"
    )
    st.stop()

with st.sidebar:
    st.subheader("Run")
    st.metric("Mode", artifact.get("mode", "?"))
    st.caption(f"Run ID: {artifact.get('run_id', '?')}")
    st.caption(f"Seed: {artifact.get('world', {}).get('seed', '?')}")
    st.divider()

    available = stages_with_routes(artifact) or ["none"]
    selected_stage = st.radio("Routes shown", options=available, index=0)

    st.divider()
    if st.button("Refresh"):
        st.rerun()

left, right = st.columns([3, 2])

with left:
    routes_for_chart = get_routes_for_stage(artifact, selected_stage)
    fig = build_grid_figure(
        world=artifact["world"],
        routes=routes_for_chart,
        stage_label=selected_stage,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Metrics")
    metrics = artifact.get("metrics")
    if metrics is None:
        st.info(
            "No metrics yet — sim scoring populates them once main.py runs the "
            "real crew (requires AMD credits)."
        )
    else:
        improvement = metrics.get("improvement_pct", {})
        cols = st.columns(3)
        cols[0].metric("Distance", f"{improvement.get('distance', 0):.1f}%", "lower")
        cols[1].metric("Time",     f"{improvement.get('time_min', 0):.1f}%", "lower")
        cols[2].metric("Energy",   f"{improvement.get('energy', 0):.1f}%", "lower")
        with st.expander("Initial vs optimized (raw)"):
            st.json(metrics)

    st.subheader("Per-stage output")
    for stage_name in ("demand", "routing", "efficiency", "disruption"):
        stage_data = artifact.get("stages", {}).get(stage_name)
        if not stage_data:
            continue
        count = len(stage_data) if isinstance(stage_data, list) else 1
        with st.expander(f"{stage_name} ({count})"):
            st.json(stage_data)
