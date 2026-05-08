"""Internal: the active World that all tools read from / write to.

CrewAI tools are stateless callables, but our tools all need a reference
to the *current* simulation. Rather than threading a World through every
tool signature (which CrewAI's tool-calling JSON wouldn't carry anyway),
main.py binds the active World once before kickoff via `set_world()`,
and each tool reads it back via `get_world()`.
"""
from __future__ import annotations

from src.sim import World

_world: World | None = None


def set_world(world: World) -> None:
    """Bind the active World. Call this in main.py before crew.kickoff()."""
    global _world
    _world = world


def get_world() -> World:
    if _world is None:
        raise RuntimeError(
            "No World is bound. Call src.tools.set_world(world) before "
            "invoking any tool (typically in main.py before crew.kickoff)."
        )
    return _world


def _reset() -> None:
    """Test-only: clear the bound World so tests can't leak state."""
    global _world
    _world = None
