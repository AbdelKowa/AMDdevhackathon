"""Tests for src.main's --placeholder path.

Placeholder mode must work without any LLM call so Person C can develop
the dashboard before AMD credits land.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src import main


def test_placeholder_artifact_has_required_top_level_keys() -> None:
    artifact = main._placeholder_artifact()
    assert set(artifact) >= {"run_id", "mode", "world", "stages", "metrics"}
    assert artifact["mode"] == "placeholder"


def test_placeholder_artifact_includes_all_baseline_stages() -> None:
    artifact = main._placeholder_artifact()
    # Disruption is intentionally absent in placeholder mode — the
    # dashboard's "before disruption" view should render from these three.
    assert set(artifact["stages"]) == {"demand", "routing", "efficiency"}


def test_write_artifact_creates_parent_dir_and_valid_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "nested" / "last_run.json"
    monkeypatch.setattr(main, "OUTPUT_PATH", target)

    main._write_artifact(main._placeholder_artifact())

    assert target.exists(), "artifact file was not created"
    payload = json.loads(target.read_text())
    assert payload["mode"] == "placeholder"
    assert "world" in payload
