"""Tests for src.sim.world.World.

The two properties the demo depends on are determinism (same seed ->
identical world) and metric monotonicity (shorter route -> better
metrics). The rest of the suite guards the public API surface.
"""
from __future__ import annotations

import pytest

from src.sim import (
    DisruptionEvent,
    Route,
    World,
    WorldState,
)


# --- Determinism: the demo and the tests both depend on this ---


def test_same_seed_produces_identical_world() -> None:
    a = World(seed=42, n_nodes=10).snapshot()
    b = World(seed=42, n_nodes=10).snapshot()
    assert a == b


def test_different_seeds_produce_different_worlds() -> None:
    a = World(seed=42, n_nodes=10).snapshot()
    b = World(seed=43, n_nodes=10).snapshot()
    assert a != b


def test_demand_is_deterministic_across_calls() -> None:
    world = World(seed=42, n_nodes=10)
    assert world.demand() == world.demand()


# --- Constructor + snapshot ---


def test_snapshot_returns_valid_world_state() -> None:
    state = World(seed=1, n_nodes=5).snapshot()
    assert isinstance(state, WorldState)
    assert state.depot.id == 0
    assert len(state.nodes) == 5
    assert {n.id for n in state.nodes} == {1, 2, 3, 4, 5}


def test_n_nodes_must_be_positive() -> None:
    with pytest.raises(ValueError, match="n_nodes must be >= 1"):
        World(seed=1, n_nodes=0)


def test_blocked_param_marks_nodes_at_construction() -> None:
    world = World(seed=1, n_nodes=5, blocked=[2, 4])
    blocked_ids = {n.id for n in world.snapshot().nodes if n.blocked}
    assert blocked_ids == {2, 4}


# --- demand() respects blocked nodes ---


def test_demand_excludes_blocked_nodes() -> None:
    world = World(seed=1, n_nodes=5, blocked=[3])
    requests = world.demand()
    assert all(r.node_id != 3 for r in requests)
    assert len(requests) == 4


# --- score() correctness + monotonicity ---


def test_score_zero_distance_for_no_routes() -> None:
    metrics = World(seed=1, n_nodes=3).score(routes=[])
    assert metrics.distance == 0
    assert metrics.time_min == 0
    assert metrics.energy == 0


def test_score_uses_manhattan_distance() -> None:
    # n_nodes=1 with seed=1 produces a known node position; route
    # depot -> node1 -> depot. We don't hardcode the exact distance
    # (RNG output may shift across Python versions); we just check it's
    # twice the one-way Manhattan distance, which is the invariant.
    world = World(seed=1, n_nodes=1)
    state = world.snapshot()
    node = state.nodes[0]
    one_way = abs(state.depot.x - node.x) + abs(state.depot.y - node.y)

    metrics = world.score([Route(vehicle_id=1, stops=[0, 1, 0])])
    assert metrics.distance == 2 * one_way


def test_shorter_route_scores_better_on_every_metric() -> None:
    """Monotonicity — the Efficiency Agent's loop relies on this."""
    world = World(seed=42, n_nodes=10)
    long_route = Route(vehicle_id=1, stops=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0])
    short_route = Route(vehicle_id=1, stops=[0, 1, 2, 0])

    long_metrics = world.score([long_route])
    short_metrics = world.score([short_route])

    assert short_metrics.distance < long_metrics.distance
    assert short_metrics.time_min < long_metrics.time_min
    assert short_metrics.energy < long_metrics.energy


def test_score_rejects_routes_with_unknown_nodes() -> None:
    world = World(seed=1, n_nodes=3)
    with pytest.raises(ValueError, match="unknown node"):
        world.score([Route(vehicle_id=1, stops=[0, 999, 0])])


# --- apply_disruption() ---


def test_apply_disruption_blocks_the_target_node() -> None:
    world = World(seed=1, n_nodes=5)
    new_state = world.apply_disruption(
        DisruptionEvent(type="road_closure", node_id=3)
    )
    blocked = next(n for n in new_state.nodes if n.id == 3)
    assert blocked.blocked is True


def test_apply_disruption_excludes_blocked_node_from_demand() -> None:
    world = World(seed=1, n_nodes=5)
    world.apply_disruption(DisruptionEvent(type="road_closure", node_id=3))
    assert all(r.node_id != 3 for r in world.demand())


def test_apply_disruption_unknown_node_id_raises() -> None:
    world = World(seed=1, n_nodes=5)
    with pytest.raises(ValueError, match="unknown node_id"):
        world.apply_disruption(
            DisruptionEvent(type="road_closure", node_id=999)
        )
