"""Tool: score a proposed list of Routes against the current world."""
from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel

from src.sim.models import Route
from src.tools._state import get_world


class _ProposeRoutesInput(BaseModel):
    routes: list[Route]


class ProposeRoutesTool(BaseTool):
    name: str = "propose_routes"
    description: str = (
        "Score a proposed plan. Pass a list of Routes (each with vehicle_id "
        "and stops starting and ending at the depot). Returns a Metrics JSON "
        "string with distance, time_min, and energy. Lower is better on every "
        "field — use this to decide whether a candidate plan beats the previous "
        "best."
    )
    args_schema: type[BaseModel] = _ProposeRoutesInput

    def _run(self, routes: list[Route] | list[dict]) -> str:
        # CrewAI normalizes args_schema-typed inputs into dicts before
        # calling _run, both from tests and from the LLM at runtime.
        # Re-validate so the sim sees real Route objects.
        validated = [Route.model_validate(r) for r in routes]
        return get_world().score(validated).model_dump_json()


propose_routes = ProposeRoutesTool()
