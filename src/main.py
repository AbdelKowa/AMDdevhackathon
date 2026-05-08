"""Crew entry point.

Wires the four agents (Demand, Routing, Efficiency, Disruption) into a
sequential CrewAI pipeline over a seeded grid world, then writes run
artifacts to output/last_run.json for the Streamlit dashboard.

Run modes:
    python -m src.main                # full demo: baseline + hardcoded disruption
    python -m src.main --baseline     # demand -> routing -> efficiency only
    python -m src.main --placeholder  # write a fake artifact, no LLM calls
                                      # (for dashboard dev before AMD credits land)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

OUTPUT_PATH = Path("output/last_run.json")
STAGE_NAMES = ["demand", "routing", "efficiency", "disruption"]


def _placeholder_world_snapshot() -> dict[str, Any]:
    """Fallback world snapshot used until src/sim/ exists."""
    return {
        "depot": {"id": 0, "x": 0, "y": 0},
        "nodes": [
            {"id": i, "x": (i * 7) % 10, "y": (i * 11) % 10, "blocked": False}
            for i in range(1, 11)
        ],
        "seed": 42,
    }


# _world_snapshot() removed: now that src/sim/ and src/tools/ both exist,
# the live path always builds a real World and binds it via set_world() so
# the tools can read/write it. See run() below.


def _parse_stage(raw: str) -> Any:
    """Best-effort JSON parse of an agent's raw output."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def _build_artifact(
    crew_result: Any,
    world: dict[str, Any],
    mode: str,
    n_stages: int,
) -> dict[str, Any]:
    task_outputs = getattr(crew_result, "tasks_output", []) or []
    stages: dict[str, Any] = {}
    for name, task_output in zip(STAGE_NAMES[:n_stages], task_outputs):
        stages[name] = _parse_stage(getattr(task_output, "raw", str(task_output)))
    return {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "world": world,
        "stages": stages,
        # Real metrics come from src/sim/ scoring; placeholder until then.
        "metrics": None,
    }


def _write_artifact(artifact: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(artifact, indent=2))
    print(f"[main] wrote {OUTPUT_PATH}")


def _placeholder_artifact() -> dict[str, Any]:
    world = _placeholder_world_snapshot()
    return {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "mode": "placeholder",
        "world": world,
        "stages": {
            "demand": [{"node_id": n["id"], "priority": 1} for n in world["nodes"]],
            "routing": [
                {"vehicle_id": 1, "stops": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]}
            ],
            "efficiency": [
                {"vehicle_id": 1, "stops": [0, 2, 4, 6, 8, 10, 9, 7, 5, 3, 1, 0]}
            ],
        },
        "metrics": {
            "initial":   {"distance": 100.0, "time_min": 60.0, "energy": 50.0},
            "optimized": {"distance":  72.0, "time_min": 44.0, "energy": 36.0},
            "improvement_pct": {"distance": 28.0, "time_min": 26.7, "energy": 28.0},
        },
    }


def run(disruption_event: dict[str, Any] | None = None) -> dict[str, Any]:
    # Deferred imports: building the agents calls amd_llm(), which requires AMD env vars.
    # Keeping these inside run() lets --placeholder work without them.
    from crewai import Crew, Process

    from src.agents.demand import demand_agent
    from src.agents.routing import routing_agent
    from src.agents.efficiency import efficiency_agent
    from src.agents.disruption import disruption_agent
    from src.sim import World
    from src.tasks.demand import demand_task
    from src.tasks.routing import routing_task
    from src.tasks.efficiency import efficiency_task
    from src.tasks.disruption import disruption_task
    from src.tools import set_world

    # Build the world once and bind it so the tools (read_world_state /
    # propose_routes / inject_disruption) all read from the same instance.
    sim_world = World(seed=42, n_nodes=20)
    set_world(sim_world)
    world = sim_world.snapshot().model_dump()
    inputs: dict[str, Any] = {"world_snapshot": world}

    if disruption_event is None:
        agents = [demand_agent, routing_agent, efficiency_agent]
        tasks = [demand_task, routing_task, efficiency_task]
        mode = "baseline"
    else:
        agents = [demand_agent, routing_agent, efficiency_agent, disruption_agent]
        tasks = [demand_task, routing_task, efficiency_task, disruption_task]
        inputs["disruption_event"] = disruption_event
        mode = "disruption"

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs=inputs)

    artifact = _build_artifact(result, world, mode, n_stages=len(tasks))
    _write_artifact(artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the delivery-logistics crew.")
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help="Write a fake output/last_run.json without any LLM call.",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Run demand -> routing -> efficiency only (no disruption).",
    )
    args = parser.parse_args()

    if args.placeholder:
        _write_artifact(_placeholder_artifact())
        return

    if args.baseline:
        run(disruption_event=None)
        return

    # Default: full demo path. The dashboard's "Trigger disruption" button
    # will later replace this hardcoded event with a real one.
    demo_event = {"type": "road_closure", "node_id": 5}
    run(disruption_event=demo_event)


if __name__ == "__main__":
    main()
