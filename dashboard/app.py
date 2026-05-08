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

import streamlit as st  # noqa: E402

from dashboard.charts import build_grid_figure  # noqa: E402
from dashboard.data import (  # noqa: E402
    DEFAULT_ARTIFACT_PATH,
    get_routes_for_stage,
    load_artifact,
    stages_with_routes,
)

st.set_page_config(
    page_title="Delivery Logistics — agent-optimized routing",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Friendlier per-stage labels for the tab UI.
STAGE_LABELS = {
    "routing": "Initial",
    "efficiency": "Optimized",
    "disruption": "Rerouted",
}

# Mode badge color + caption keyed off the artifact's "mode" field.
MODE_STYLES: dict[str, tuple[str, str]] = {
    "placeholder": ("#9E9E9E", "Synthetic data — no LLM call"),
    "baseline":    ("#4FC3F7", "Three-stage crew, no disruption"),
    "disruption":  ("#ED1C24", "Full crew including disruption response"),
}

# Minimal CSS to tighten typography and add a chip style for the mode badge.
st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      h1 { font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
      .subtitle { color: #9AA0A6; font-size: 0.95rem; margin-bottom: 1rem; }
      .mode-chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #0E1117;
      }
      .mode-caption { color: #9AA0A6; font-size: 0.85rem; margin-left: 8px; }
      [data-testid="stMetric"] { background: #1A1D24; padding: 12px; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Delivery Logistics")
st.markdown(
    "<div class='subtitle'>Multi-agent routing on AMD Developer Cloud · "
    "CrewAI · SGLang · Llama-3.1-8B</div>",
    unsafe_allow_html=True,
)

artifact = load_artifact()
if artifact is None:
    st.warning(
        f"No artifact found at `{DEFAULT_ARTIFACT_PATH}`. Generate one with:\n\n"
        "```\npython -m src.main --placeholder\n```"
    )
    st.stop()

# Mode chip + caption beside the title.
mode = artifact.get("mode", "?")
chip_color, mode_caption = MODE_STYLES.get(mode, ("#9E9E9E", ""))
st.markdown(
    f"<span class='mode-chip' style='background:{chip_color}'>{mode}</span>"
    f"<span class='mode-caption'>{mode_caption}</span>",
    unsafe_allow_html=True,
)
st.write("")  # vertical spacer

with st.sidebar:
    st.subheader("Run")
    st.caption(f"**Run ID**\n\n`{artifact.get('run_id', '?')}`")
    st.caption(f"**Seed**\n\n`{artifact.get('world', {}).get('seed', '?')}`")
    st.caption(
        f"**Nodes**\n\n`{len(artifact.get('world', {}).get('nodes', []))}` "
        f"delivery + 1 depot"
    )
    st.divider()
    if st.button("Refresh", use_container_width=True):
        st.rerun()
    st.caption(
        "After running `python -m src.main`, click Refresh to load the new "
        "artifact."
    )

left, right = st.columns([3, 2], gap="large")

with left:
    available = stages_with_routes(artifact)
    if not available:
        st.info("No routes in the artifact yet — only world state to display.")
        st.plotly_chart(
            build_grid_figure(world=artifact["world"]),
            use_container_width=True,
        )
    else:
        tab_objects = st.tabs([STAGE_LABELS.get(s, s) for s in available])
        for tab, stage in zip(tab_objects, available):
            with tab:
                fig = build_grid_figure(
                    world=artifact["world"],
                    routes=get_routes_for_stage(artifact, stage),
                    stage_label=STAGE_LABELS.get(stage, stage),
                )
                st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Improvement")
    metrics = artifact.get("metrics")
    if metrics is None:
        st.info(
            "No metrics yet — sim scoring populates them once main.py runs "
            "the real crew (requires AMD credits)."
        )
    else:
        improvement = metrics.get("improvement_pct", {})
        cols = st.columns(3)
        cols[0].metric(
            "Distance ↓", f"{improvement.get('distance', 0):.1f}%",
        )
        cols[1].metric(
            "Time ↓", f"{improvement.get('time_min', 0):.1f}%",
        )
        cols[2].metric(
            "Energy ↓", f"{improvement.get('energy', 0):.1f}%",
        )
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
