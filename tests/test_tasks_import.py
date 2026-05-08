"""Smoke tests: tasks import, are bound to the right agents, and chain correctly."""
from __future__ import annotations

from src.tasks.demand import demand_task
from src.tasks.routing import routing_task
from src.tasks.efficiency import efficiency_task
from src.tasks.disruption import disruption_task


def test_tasks_are_bound_to_the_correct_agents() -> None:
    assert demand_task.agent.role == "Delivery Demand Planner"
    assert routing_task.agent.role == "Initial Route Planner"
    assert efficiency_task.agent.role == "Route Efficiency Optimizer"
    assert disruption_task.agent.role == "Real-time Disruption Responder"


def test_context_chain_is_demand_routing_efficiency_disruption() -> None:
    # demand has no upstream — CrewAI stores a NOT_SPECIFIED sentinel for
    # unset context, so check "no upstream tasks" rather than falsiness.
    assert not isinstance(demand_task.context, list) or not demand_task.context

    # Each subsequent task receives exactly the previous task as context.
    assert routing_task.context == [demand_task]
    assert efficiency_task.context == [routing_task]
    assert disruption_task.context == [efficiency_task]


def test_task_descriptions_reference_required_inputs() -> None:
    # main.py passes world_snapshot to every kickoff and disruption_event
    # only when triggering the disruption stage. The prompts must reference
    # those keys or CrewAI's input substitution will silently no-op.
    assert "{world_snapshot}" in demand_task.description
    assert "{world_snapshot}" in routing_task.description
    assert "{disruption_event}" in disruption_task.description
    assert "{world_snapshot}" in disruption_task.description
