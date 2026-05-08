"""Seeded 2D-grid world the agents act on.

Pure Python, no LLM. Deterministic given a seed: the same (seed, n_nodes,
blocked) inputs always produce the same world, demand list, and metrics.
This is what makes the demo reproducible and the regression tests sharp.
"""
from __future__ import annotations

import random

from src.sim.models import (
    DeliveryRequest,
    DisruptionEvent,
    Metrics,
    Node,
    Route,
    WorldState,
)

# Nodes spawn at integer coords in [0, GRID_SIZE).
GRID_SIZE = 20

# Per-unit-distance proxies. Tuned so a shorter route monotonically
# beats a longer one on every metric, which is what the Efficiency
# Agent's optimization loop and the dashboard's "% improvement" both
# depend on.
TIME_MIN_PER_UNIT = 1.5
ENERGY_PER_UNIT = 0.5


class World:
    """Seeded grid + depot + delivery nodes + scoring + disruption.

    Args:
        seed: RNG seed. Same seed -> identical world.
        n_nodes: number of delivery nodes (depot is always id=0, separate).
        blocked: node ids that start out blocked.
    """

    def __init__(
        self,
        seed: int,
        n_nodes: int,
        blocked: list[int] | None = None,
    ) -> None:
        if n_nodes < 1:
            raise ValueError(f"n_nodes must be >= 1, got {n_nodes}")
        self._seed = seed
        self._depot = Node(id=0, x=0, y=0, blocked=False)
        rng = random.Random(seed)
        blocked_set = set(blocked or [])
        self._nodes = [
            Node(
                id=i,
                x=rng.randint(0, GRID_SIZE - 1),
                y=rng.randint(0, GRID_SIZE - 1),
                blocked=(i in blocked_set),
            )
            for i in range(1, n_nodes + 1)
        ]
        # Pre-compute priorities so demand() is deterministic across calls.
        self._priorities = {n.id: rng.randint(1, 3) for n in self._nodes}

    def snapshot(self) -> WorldState:
        return WorldState(
            depot=self._depot,
            nodes=list(self._nodes),
            seed=self._seed,
        )

    def demand(self) -> list[DeliveryRequest]:
        return [
            DeliveryRequest(node_id=n.id, priority=self._priorities[n.id])
            for n in self._nodes
            if not n.blocked
        ]

    def score(self, routes: list[Route]) -> Metrics:
        positions = {n.id: (n.x, n.y) for n in (self._depot, *self._nodes)}
        total_distance = 0.0
        for route in routes:
            for src_id, dst_id in zip(route.stops, route.stops[1:]):
                if src_id not in positions or dst_id not in positions:
                    raise ValueError(
                        f"route {route.vehicle_id} references unknown node "
                        f"({src_id} -> {dst_id})"
                    )
                ax, ay = positions[src_id]
                bx, by = positions[dst_id]
                # Manhattan distance — natural for a grid where you can't
                # cut diagonally between blocks.
                total_distance += abs(ax - bx) + abs(ay - by)
        return Metrics(
            distance=total_distance,
            time_min=total_distance * TIME_MIN_PER_UNIT,
            energy=total_distance * ENERGY_PER_UNIT,
        )

    def apply_disruption(self, event: DisruptionEvent) -> WorldState:
        # v1: every event type blocks the target node. The Disruption Agent
        # sees the new snapshot and reroutes around it. Type-specific
        # behavior (e.g. traffic = time penalty without blocking) is a v2.
        for i, node in enumerate(self._nodes):
            if node.id == event.node_id:
                self._nodes[i] = node.model_copy(update={"blocked": True})
                return self.snapshot()
        raise ValueError(f"unknown node_id: {event.node_id}")
