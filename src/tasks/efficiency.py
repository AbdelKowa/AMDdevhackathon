"""Efficiency Task — rewrites initial Routes for shorter, cheaper, faster delivery."""
from __future__ import annotations

from crewai import Task

from src.agents.efficiency import efficiency_agent
from src.tasks.routing import routing_task

# TODO(Person A/B): wire output_pydantic once src/sim/models.py exists.
# from src.sim.models import Route

efficiency_task = Task(
    description=(
        "Take the initial Routes produced by the Routing Agent and rewrite "
        "them to minimize total distance, estimated delivery time, and "
        "energy use.\n\n"
        "Use the propose_routes tool to score each candidate plan. Only "
        "commit to a change if the new Metrics strictly improve on the "
        "previous best. Do not drop deliveries. Do not visit blocked nodes. "
        "Every route must still start and end at the depot."
    ),
    expected_output=(
        "A JSON array of optimized Route objects in the same schema as the "
        "Routing Agent's output. Return only the JSON array, no prose."
    ),
    agent=efficiency_agent,
    context=[routing_task],
    # output_pydantic=list[Route],
)
