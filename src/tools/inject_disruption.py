"""Tool: apply a DisruptionEvent to the world (used by the Disruption Agent)."""
from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel

from src.sim.models import DisruptionEvent
from src.tools._state import get_world


class _InjectDisruptionInput(BaseModel):
    event: DisruptionEvent


class InjectDisruptionTool(BaseTool):
    name: str = "inject_disruption"
    description: str = (
        "Apply a DisruptionEvent (road_closure, traffic, or delay) to the "
        "world. Returns the updated WorldState as a JSON string. The target "
        "node is marked as blocked, so subsequent reads / scores will see it "
        "as impassable."
    )
    args_schema: type[BaseModel] = _InjectDisruptionInput

    def _run(self, event: DisruptionEvent | dict) -> str:
        # CrewAI normalizes args_schema-typed inputs into dicts before
        # calling _run. Re-validate so the sim sees a real DisruptionEvent.
        validated = DisruptionEvent.model_validate(event)
        return get_world().apply_disruption(validated).model_dump_json()


inject_disruption = InjectDisruptionTool()
