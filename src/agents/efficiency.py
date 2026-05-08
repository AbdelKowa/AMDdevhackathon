"""Efficiency Agent — rewrites initial routes for shorter, cheaper, faster delivery."""
from __future__ import annotations

from crewai import Agent

from src.llm import amd_llm

# TODO(Person A/B): import once src/tools/ exists.
# from src.tools.propose_routes import propose_routes

efficiency_agent = Agent(
    role="Route Efficiency Optimizer",
    goal=(
        "Take the initial routes from the Routing Agent and rewrite them to "
        "minimize total distance, estimated delivery time, and energy use, "
        "without dropping any delivery or violating depot start/end."
    ),
    backstory=(
        "You are an operations researcher who lives for shaving miles off a "
        "route. You compare every candidate plan against the previous one "
        "using the Metrics returned by propose_routes, and you only commit "
        "to a change if it strictly improves the totals."
    ),
    tools=[
        # propose_routes,
    ],
    llm=amd_llm(),
    allow_delegation=False,
    verbose=True,
)
