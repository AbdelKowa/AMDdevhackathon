"""Demand Task — surveys the world snapshot and produces DeliveryRequests."""
from __future__ import annotations

from crewai import Task

from src.agents.demand import demand_agent

# TODO(Person A/B): wire output_pydantic once src/sim/models.py exists.
# from src.sim.models import DeliveryRequest

demand_task = Task(
    description=(
        "You are given the current world snapshot:\n\n"
        "{world_snapshot}\n\n"
        "Identify every active, reachable delivery node in the snapshot and "
        "produce one DeliveryRequest per node. Do not invent nodes. Do not "
        "include nodes flagged as blocked. Do not duplicate requests."
    ),
    expected_output=(
        "A JSON array of DeliveryRequest objects. Each object must contain "
        "at minimum: node_id (int), priority (int, 1=highest), and any "
        "fields required by the simulation's DeliveryRequest schema. "
        "Return only the JSON array, no prose."
    ),
    agent=demand_agent,
    # output_pydantic=list[DeliveryRequest],
)
