"""Routing Agent — turns demand into an initial set of feasible routes."""
from __future__ import annotations

from crewai import Agent

from src.llm import amd_llm

# TODO(Person A/B): import once src/tools/ exists.
# from src.tools.read_world_state import read_world_state
# from src.tools.propose_routes import propose_routes

routing_agent = Agent(
    role="Initial Route Planner",
    goal=(
        "Given the DeliveryRequests from the Demand Agent and the world "
        "snapshot, produce a feasible initial set of Routes that start and "
        "end at the depot and visit every requested node exactly once."
    ),
    backstory=(
        "You are a dispatch coordinator. Your first pass does not need to be "
        "optimal — the Efficiency Agent will refine it — but it must be "
        "valid: no blocked nodes, every delivery covered, every route "
        "returns to the depot."
    ),
    tools=[
        # read_world_state,
        # propose_routes,
    ],
    llm=amd_llm(),
    allow_delegation=False,
    verbose=True,
)
