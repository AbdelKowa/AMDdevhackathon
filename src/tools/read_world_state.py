"""Tool: dump the current world snapshot as JSON for an agent to read."""
from __future__ import annotations

from crewai.tools import BaseTool

from src.tools._state import get_world


class ReadWorldStateTool(BaseTool):
    name: str = "read_world_state"
    description: str = (
        "Return the current world snapshot (depot + delivery nodes + blocked "
        "flags + seed) as a JSON string. Take no arguments. Use this whenever "
        "you need to know which nodes exist, where they are, and which are "
        "currently passable."
    )

    def _run(self) -> str:
        return get_world().snapshot().model_dump_json()


read_world_state = ReadWorldStateTool()
