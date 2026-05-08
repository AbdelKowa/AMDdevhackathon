"""Disruption Task — reroutes optimized Routes around a live event."""
from __future__ import annotations

from crewai import Task

from src.agents.disruption import disruption_agent
from src.tasks.efficiency import efficiency_task

# TODO(Person A/B): wire output_pydantic once src/sim/models.py exists.
# from src.sim.models import Route

disruption_task = Task(
    description=(
        "A disruption has occurred. Event details:\n\n"
        "{disruption_event}\n\n"
        "Take the optimized Routes from the Efficiency Agent and patch only "
        "the routes that touch the affected node(s). Leave unaffected legs "
        "untouched — do not throw away the Efficiency Agent's work. Use the "
        "current world snapshot to find valid detours:\n\n"
        "{world_snapshot}\n\n"
        "Every patched route must still start and end at the depot, cover "
        "all of its original deliveries, and avoid the disrupted node(s)."
    ),
    expected_output=(
        "A JSON array of rerouted Route objects in the same schema as the "
        "Efficiency Agent's output. Return only the JSON array, no prose."
    ),
    agent=disruption_agent,
    context=[efficiency_task],
    # output_pydantic=list[Route],
)
