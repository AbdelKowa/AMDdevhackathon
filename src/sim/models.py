"""Pydantic models for the simulation.

These are the contract between the sim (`src/sim/`), the tools that wrap
it (`src/tools/`), and the agents that consume them (`src/agents/`,
`src/tasks/`). Field names match what's already referenced in the agent
task prompts and in main.py's placeholder artifact — change them here
without coordinating and you'll silently break the agents.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Node(BaseModel):
    """A single point on the 2D grid (depot or delivery node)."""

    id: int
    x: int
    y: int
    blocked: bool = False


class WorldState(BaseModel):
    """Snapshot of the world the agents see at one moment in time."""

    depot: Node
    nodes: list[Node]
    seed: int


class DeliveryRequest(BaseModel):
    """A single delivery the routing pipeline needs to plan for."""

    node_id: int
    priority: int = Field(ge=1, description="1 = highest priority")


class Route(BaseModel):
    """A vehicle's planned path: depot -> ... -> depot."""

    vehicle_id: int
    stops: list[int]

    @field_validator("stops")
    @classmethod
    def _must_start_and_end_at_same_node(cls, stops: list[int]) -> list[int]:
        if len(stops) < 2:
            raise ValueError("route must have at least 2 stops (depot start + end)")
        if stops[0] != stops[-1]:
            raise ValueError(
                f"route must return to its starting node; "
                f"got start={stops[0]}, end={stops[-1]}"
            )
        return stops


class Metrics(BaseModel):
    """Score for a set of routes. Lower is better on every field."""

    distance: float = Field(ge=0)
    time_min: float = Field(ge=0)
    energy: float = Field(ge=0)


class DisruptionEvent(BaseModel):
    """A live event the Disruption Agent has to react to."""

    type: Literal["road_closure", "traffic", "delay"]
    node_id: int
