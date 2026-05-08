"""Tests for src.tools.*.

Tools wrap the World API so the agents never import from src/sim/ directly.
The module-level world binding (set_world) means tests must reset state
between cases — handled by the autouse fixture below.
"""
from __future__ import annotations

import json

import pytest

from src.sim import DisruptionEvent, Route, World
from src.tools import (
    inject_disruption,
    propose_routes,
    read_world_state,
    set_world,
)
from src.tools import _state


@pytest.fixture(autouse=True)
def _clear_bound_world() -> None:
    yield
    _state._reset()


# --- Each tool should fail loudly if no World is bound ---


def test_read_world_state_raises_without_bound_world() -> None:
    with pytest.raises(RuntimeError, match="No World is bound"):
        read_world_state.run()


def test_propose_routes_raises_without_bound_world() -> None:
    with pytest.raises(RuntimeError, match="No World is bound"):
        propose_routes.run(routes=[Route(vehicle_id=1, stops=[0, 1, 0])])


def test_inject_disruption_raises_without_bound_world() -> None:
    with pytest.raises(RuntimeError, match="No World is bound"):
        inject_disruption.run(
            event=DisruptionEvent(type="road_closure", node_id=1)
        )


# --- Happy paths ---


def test_read_world_state_returns_snapshot_json() -> None:
    set_world(World(seed=1, n_nodes=3))
    payload = json.loads(read_world_state.run())
    assert payload["depot"]["id"] == 0
    assert len(payload["nodes"]) == 3
    assert payload["seed"] == 1


def test_propose_routes_returns_metrics_json() -> None:
    set_world(World(seed=1, n_nodes=3))
    payload = json.loads(
        propose_routes.run(routes=[Route(vehicle_id=1, stops=[0, 1, 0])])
    )
    assert {"distance", "time_min", "energy"} <= set(payload)
    assert payload["distance"] >= 0


def test_inject_disruption_blocks_node_and_returns_updated_state() -> None:
    world = World(seed=1, n_nodes=3)
    set_world(world)
    payload = json.loads(
        inject_disruption.run(
            event=DisruptionEvent(type="road_closure", node_id=2)
        )
    )
    blocked = next(n for n in payload["nodes"] if n["id"] == 2)
    assert blocked["blocked"] is True
    # The bound World should also reflect the change (tools mutate, not copy).
    assert all(r.node_id != 2 for r in world.demand())


# --- Agents have the tools wired up ---


def test_each_agent_has_its_expected_tools() -> None:
    from src.agents.demand import demand_agent
    from src.agents.routing import routing_agent
    from src.agents.efficiency import efficiency_agent
    from src.agents.disruption import disruption_agent

    expected = {
        "Delivery Demand Planner": {"read_world_state"},
        "Initial Route Planner": {"read_world_state", "propose_routes"},
        "Route Efficiency Optimizer": {"propose_routes"},
        "Real-time Disruption Responder": {"read_world_state", "propose_routes"},
    }
    for agent in (demand_agent, routing_agent, efficiency_agent, disruption_agent):
        assert {t.name for t in agent.tools} == expected[agent.role]
