"""Smoke tests: every agent imports and has the expected wiring."""
from __future__ import annotations

from src.agents.demand import demand_agent
from src.agents.routing import routing_agent
from src.agents.efficiency import efficiency_agent
from src.agents.disruption import disruption_agent

EXPECTED_ROLES = {
    "demand": "Delivery Demand Planner",
    "routing": "Initial Route Planner",
    "efficiency": "Route Efficiency Optimizer",
    "disruption": "Real-time Disruption Responder",
}


def test_all_agents_have_expected_roles() -> None:
    actual = {
        "demand": demand_agent.role,
        "routing": routing_agent.role,
        "efficiency": efficiency_agent.role,
        "disruption": disruption_agent.role,
    }
    assert actual == EXPECTED_ROLES


def test_all_agents_have_an_llm_attached() -> None:
    for agent in (demand_agent, routing_agent, efficiency_agent, disruption_agent):
        assert agent.llm is not None, f"{agent.role} has no LLM"


def test_no_agent_allows_delegation() -> None:
    # The pipeline is sequential; delegation between agents would bypass
    # the task chain and surprise the dashboard's per-stage rendering.
    for agent in (demand_agent, routing_agent, efficiency_agent, disruption_agent):
        assert agent.allow_delegation is False, f"{agent.role} has delegation enabled"
