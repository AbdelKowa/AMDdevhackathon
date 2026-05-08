"""CrewAI Agent definitions. One file per agent.

Agents reach the simulation only through `src/tools/` — never import from
`src/sim/` here. See docs/architecture.md.

Import agents directly from their submodule (e.g.
`from src.agents.demand import demand_agent`) so each LLM client is
constructed only when actually used.
"""
