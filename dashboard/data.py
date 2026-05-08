"""Pure-Python helpers for loading and slicing the run artifact.

Keeping these out of `app.py` lets us unit-test them without spinning up
a Streamlit context.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT_PATH = Path("output/last_run.json")

# Canonical stage order, refined -> raw. best_available_routes() walks this.
_STAGE_PREFERENCE = ("disruption", "efficiency", "routing")


def load_artifact(path: Path = DEFAULT_ARTIFACT_PATH) -> dict[str, Any] | None:
    """Read the latest run artifact, or None if it doesn't exist yet."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def get_routes_for_stage(artifact: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    """Pull the route list for a given stage, or [] if absent."""
    routes = artifact.get("stages", {}).get(stage)
    return routes if isinstance(routes, list) else []


def best_available_routes(
    artifact: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    """Most refined routes available: disruption > efficiency > routing > none.

    Used as the dashboard's default "show me the latest" view.
    """
    for stage in _STAGE_PREFERENCE:
        routes = get_routes_for_stage(artifact, stage)
        if routes:
            return stage, routes
    return "none", []


def stages_with_routes(artifact: dict[str, Any]) -> list[str]:
    """Stage names (in canonical order) that have at least one route."""
    return [s for s in _STAGE_PREFERENCE if get_routes_for_stage(artifact, s)]
