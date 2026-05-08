"""Tests for the sim pydantic models.

These are the contract between sim, tools, and agents. Validator failures
here are the cheapest way to catch bad data before it reaches the LLM
or the dashboard.
"""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from src.sim.models import (
    DeliveryRequest,
    DisruptionEvent,
    Metrics,
    Node,
    Route,
    WorldState,
)


# --- Field-name checks: must match what main.py and the task prompts assume ---


def test_world_state_matches_main_py_placeholder_shape() -> None:
    """main.py._placeholder_world_snapshot() emits this shape; agents read it."""
    payload = {
        "depot": {"id": 0, "x": 0, "y": 0, "blocked": False},
        "nodes": [{"id": 1, "x": 7, "y": 1, "blocked": False}],
        "seed": 42,
    }
    state = WorldState.model_validate(payload)
    assert state.depot.id == 0
    assert state.nodes[0].id == 1
    assert state.seed == 42


def test_main_py_placeholder_world_snapshot_validates() -> None:
    """Cross-team contract: main.py's actual placeholder output must validate.

    If this breaks, either Person A changed the snapshot shape or Person B
    changed the model field names — they need to talk before merging.
    """
    from src import main

    state = WorldState.model_validate(main._placeholder_world_snapshot())
    assert state.depot.id == 0
    assert len(state.nodes) > 0


def test_disruption_event_matches_main_py_demo_event() -> None:
    """main.py hardcodes {'type': 'road_closure', 'node_id': 5} as the demo event."""
    event = DisruptionEvent.model_validate({"type": "road_closure", "node_id": 5})
    assert event.type == "road_closure"
    assert event.node_id == 5


# --- Validator behavior ---


def test_route_must_return_to_start() -> None:
    Route(vehicle_id=1, stops=[0, 1, 2, 0])  # ok
    with pytest.raises(ValidationError, match="return to its starting node"):
        Route(vehicle_id=1, stops=[0, 1, 2, 3])


def test_route_rejects_too_few_stops() -> None:
    with pytest.raises(ValidationError, match="at least 2 stops"):
        Route(vehicle_id=1, stops=[0])


def test_delivery_request_priority_must_be_positive() -> None:
    DeliveryRequest(node_id=1, priority=1)  # ok
    with pytest.raises(ValidationError):
        DeliveryRequest(node_id=1, priority=0)


def test_metrics_reject_negative_values() -> None:
    Metrics(distance=0.0, time_min=0.0, energy=0.0)  # ok
    with pytest.raises(ValidationError):
        Metrics(distance=-1.0, time_min=10.0, energy=10.0)


# --- JSON roundtrip (every model crosses the agent-tool boundary as JSON) ---


@pytest.mark.parametrize(
    "instance",
    [
        Node(id=3, x=4, y=5, blocked=True),
        DeliveryRequest(node_id=7, priority=2),
        Route(vehicle_id=1, stops=[0, 2, 4, 0]),
        Metrics(distance=12.5, time_min=8.0, energy=4.2),
        DisruptionEvent(type="traffic", node_id=9),
    ],
)
def test_models_roundtrip_through_json(instance) -> None:  # type: ignore[no-untyped-def]
    payload = json.loads(instance.model_dump_json())
    rebuilt = type(instance).model_validate(payload)
    assert rebuilt == instance
