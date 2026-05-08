"""Routing Task — turns DeliveryRequests into an initial set of feasible Routes."""
from __future__ import annotations

from crewai import Task

from src.agents.routing import routing_agent
from src.tasks.demand import demand_task

# TODO(Person A/B): wire output_pydantic once src/sim/models.py exists.
# from src.sim.models import Route

routing_task = Task(
    description=(
        "Using the DeliveryRequests produced by the Demand Agent and the "
        "world snapshot:\n\n"
        "{world_snapshot}\n\n"
        "Build an initial set of Routes that (a) start and end at the depot, "
        "(b) cover every requested node exactly once, and (c) avoid blocked "
        "nodes. Feasibility matters here, not optimality — the Efficiency "
        "Agent will refine the plan."
    ),
    expected_output=(
        "A JSON array of Route objects. Each Route must contain: "
        "vehicle_id (int) and a stops field (ordered list of node_ids "
        "starting and ending with the depot). Return only the JSON array, "
        "no prose."
    ),
    agent=routing_agent,
    context=[demand_task],
    # output_pydantic=list[Route],
)
