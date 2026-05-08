"""CrewAI tool wrappers around the simulation API.

Agents reach the simulation only through these tools — never by importing
from `src/sim/` directly. Each tool reads/writes the active World bound
via `set_world()`. main.py is the canonical caller of `set_world()`.
"""
from src.tools._state import set_world
from src.tools.inject_disruption import inject_disruption
from src.tools.propose_routes import propose_routes
from src.tools.read_world_state import read_world_state

__all__ = [
    "inject_disruption",
    "propose_routes",
    "read_world_state",
    "set_world",
]
