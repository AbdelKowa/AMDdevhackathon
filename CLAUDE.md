# CLAUDE.md

Working notes for Claude Code. Human-facing setup, branching, PR flow, cost rules, and the demo timeline live in [`README.md`](README.md) — defer to it for those.

## Project
A multi-agent AI system that simulates and optimizes delivery logistics in real time. Built for the lablab.ai AMD Developer Hackathon, Track 1, May 4–10, 2026. Concept and demo flow live in [`project-overview.md`](project-overview.md). Architecture and the agents↔tools↔sim contract live in [`docs/architecture.md`](docs/architecture.md). **Read both before making non-trivial changes.**

> **Naming:** the team has not picked a final project name. Don't introduce a working title in code, docs, commits, or PR descriptions — refer to it generically ("the project", "the crew", "the system") until a name is locked.

## Stack
- **CrewAI** for agent orchestration.
- **Open-source models** (Llama 3 / Mistral) on AMD Developer Cloud, accessed via an **OpenAI-compatible API**. Use the factory in `src/llm.py` rather than instantiating clients ad-hoc.
- **Streamlit** for the dashboard.
- Python 3.11+, virtual env at `.venv/`.

## Code layout
- `src/agents/` — CrewAI Agent definitions (role, goal, backstory, tools). One file per agent.
- `src/tasks/` — CrewAI Task definitions. One file per task.
- `src/tools/` — Custom tools agents call. Tools are the *only* path from agents into the simulation.
- `src/sim/` — Simulation engine. Pure Python, no LLM calls. Owned by Person B.
- `src/llm.py` — AMD LLM client factory. **Always import from here**; never construct LLM clients inline.
- `src/main.py` — Crew assembly and `kickoff()`. Demo entry point.
- `dashboard/` — Streamlit UI.
- `notebooks/` — Scratch exploration. Don't import from `notebooks/` in `src/`.
- `tests/` — Pytest. Mirror the source layout.

## Cross-file invariants
- **Agents reach the simulation only through `src/tools/`.** Never import from `src/sim/` inside `src/agents/` or `src/tasks/`.
- **All LLM construction goes through `src/llm.py`.** This is the single place to flip models, swap endpoints, or add tracing.
- **Environment loading** — call `load_dotenv()` once at the top of `src/main.py` (and in `src/llm.py` for standalone use). Don't sprinkle it elsewhere.
- **Run artifacts** go to `output/` (gitignored). The dashboard reads from `output/last_run.json`.

## When working in this repo
- Read `project-overview.md` and `docs/architecture.md` before adding features.
- Stay inside the active owner's boundary unless coordinating (see the ownership table in README).
- For UI/Streamlit changes, run the dashboard locally and click through the demo flow before declaring the work done. Type-checks and unit tests don't catch visual regressions.
- Tests go in `tests/`, mirror the source layout. Run `pytest` before opening a PR.
- Cost discipline is set by the team in README — when iterating, default to the 8B dev model and don't run the full crew in tight loops.

## Claude Code help / feedback
- `/help` — get help with using Claude Code
- File issues at https://github.com/anthropics/claude-code/issues
