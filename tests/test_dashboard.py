"""Tests for the dashboard data + charts helpers.

Streamlit-side `app.py` isn't unit-testable without a running app context,
so the testable logic lives in `dashboard/data.py` and `dashboard/charts.py`
as pure functions. These tests cover all the behavior the demo depends on.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard.charts import build_grid_figure
from dashboard.data import (
    best_available_routes,
    get_routes_for_stage,
    load_artifact,
    stages_with_routes,
)


@pytest.fixture
def sample_artifact() -> dict:
    return {
        "run_id": "2026-05-08T00:00:00",
        "mode": "placeholder",
        "world": {
            "depot": {"id": 0, "x": 0, "y": 0, "blocked": False},
            "nodes": [
                {"id": 1, "x": 5, "y": 5, "blocked": False},
                {"id": 2, "x": 10, "y": 10, "blocked": True},
                {"id": 3, "x": 3, "y": 8, "blocked": False},
            ],
            "seed": 42,
        },
        "stages": {
            "demand": [{"node_id": 1, "priority": 1}],
            "routing": [{"vehicle_id": 1, "stops": [0, 1, 3, 0]}],
            "efficiency": [{"vehicle_id": 1, "stops": [0, 3, 1, 0]}],
        },
        "metrics": {
            "initial":   {"distance": 100.0, "time_min": 60.0, "energy": 50.0},
            "optimized": {"distance":  80.0, "time_min": 48.0, "energy": 40.0},
            "improvement_pct": {"distance": 20.0, "time_min": 20.0, "energy": 20.0},
        },
    }


# --- data.load_artifact ---


def test_load_artifact_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_artifact(tmp_path / "missing.json") is None


def test_load_artifact_reads_existing_file(
    tmp_path: Path, sample_artifact: dict
) -> None:
    target = tmp_path / "last_run.json"
    target.write_text(json.dumps(sample_artifact))
    assert load_artifact(target) == sample_artifact


# --- data.get_routes_for_stage ---


def test_get_routes_for_stage_returns_routes(sample_artifact: dict) -> None:
    assert get_routes_for_stage(sample_artifact, "routing") == [
        {"vehicle_id": 1, "stops": [0, 1, 3, 0]}
    ]


def test_get_routes_for_stage_returns_empty_list_when_missing(
    sample_artifact: dict,
) -> None:
    assert get_routes_for_stage(sample_artifact, "disruption") == []


# --- data.best_available_routes ---


def test_best_available_routes_prefers_disruption(sample_artifact: dict) -> None:
    sample_artifact["stages"]["disruption"] = [{"vehicle_id": 1, "stops": [0, 2, 0]}]
    stage, _ = best_available_routes(sample_artifact)
    assert stage == "disruption"


def test_best_available_routes_falls_back_to_efficiency(
    sample_artifact: dict,
) -> None:
    stage, _ = best_available_routes(sample_artifact)
    assert stage == "efficiency"


def test_best_available_routes_returns_none_when_no_stages(
    sample_artifact: dict,
) -> None:
    sample_artifact["stages"] = {}
    stage, routes = best_available_routes(sample_artifact)
    assert stage == "none"
    assert routes == []


# --- data.stages_with_routes ---


def test_stages_with_routes_lists_present_stages(sample_artifact: dict) -> None:
    assert stages_with_routes(sample_artifact) == ["efficiency", "routing"]


# --- charts.build_grid_figure ---


def test_build_grid_figure_renders_with_no_routes(sample_artifact: dict) -> None:
    fig = build_grid_figure(world=sample_artifact["world"])
    # open nodes + blocked nodes + depot = 3 traces minimum
    assert len(fig.data) >= 3


def test_build_grid_figure_renders_route_traces(sample_artifact: dict) -> None:
    fig = build_grid_figure(
        world=sample_artifact["world"],
        routes=sample_artifact["stages"]["routing"],
        stage_label="routing",
    )
    # Adds one trace per route on top of the node traces.
    assert len(fig.data) >= 4
    assert fig.layout.title.text == "Stage: routing"


def test_build_grid_figure_handles_empty_world() -> None:
    fig = build_grid_figure(
        world={"depot": {"id": 0, "x": 0, "y": 0, "blocked": False}, "nodes": []},
    )
    # Just the depot trace.
    assert len(fig.data) == 1


def test_build_grid_figure_renders_real_main_artifact() -> None:
    """Cross-team smoke test: feed main.py's actual placeholder artifact in."""
    from src import main

    artifact = main._placeholder_artifact()
    fig = build_grid_figure(
        world=artifact["world"],
        routes=artifact["stages"]["efficiency"],
        stage_label="efficiency",
    )
    assert fig is not None
    assert len(fig.data) >= 3
