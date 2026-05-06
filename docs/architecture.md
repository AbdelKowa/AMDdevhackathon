# Architecture — AI agents for delivery logistics optimization (name TBD)

> **Status:** Draft v1, May 5 2026. Owners should ratify or amend before locking interfaces.
> **Scope:** how the four agents, the simulation, the LLM, and the dashboard fit together.
> **Non-goals:** product pitch (see `project-overview.md`), team workflow (see `CLAUDE.md`).

---

## 1. System overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Streamlit Dashboard                       │
│  (live grid, routes, metrics, disruption controls)  — Person C   │
└─────────────────────────┬────────────────────────────────────────┘
                          │ reads run state
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                       src/main.py — Crew                          │
│  CrewAI orchestrates the four agents in a sequential pipeline.    │
└──┬──────────┬───────────┬───────────┬─────────────────────────────┘
   │          │           │           │
   ▼          ▼           ▼           ▼
 Demand    Routing    Efficiency  Disruption       — Person A
 Agent      Agent      Agent       Agent
   │          │           │           │
   └──────────┴─────┬─────┴───────────┘
                    │ tool calls (read state, propose plan, accept event)
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│              src/tools/ — thin wrappers around sim API           │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│  src/sim/ — Grid, routes, metrics, disruption engine              │
│  Pure Python. No LLM calls. Deterministic given a seed. — Person B│
└──────────────────────────────────────────────────────────────────┘

LLM access (all agents) ──► src/llm.py ──► AMD Developer Cloud
                                            (OpenAI-compatible API)
```

The hard line in this diagram is **agents never import from `src/sim/` directly**. They go through `src/tools/`. That keeps the simulation testable in isolation and lets Person B refactor sim internals without breaking agents.

---

## 2. Components

### 2.1 Simulation (`src/sim/`) — Person B
Pure Python, no LLM. The world the agents act on.

**Responsibilities:**
- 2D grid map (1 depot + 10–30 delivery nodes, optional blocked nodes).
- Route representation and validation (sequence of grid nodes from depot back to depot).
- Metrics calculation: total distance, estimated time, energy/fuel proxy.
- Disruption engine: inject road closures, traffic, delays at runtime.
- Deterministic: given a seed, the same scenario reproduces.

**Public API (Person B owns the final shape — this is the proposed contract):**

```python
# src/sim/__init__.py — re-exports
World(seed: int, n_nodes: int, blocked: list[Node] = []) -> World

world.snapshot() -> WorldState           # serialize current state for agents
world.demand() -> list[DeliveryRequest]  # what needs to ship
world.score(routes: list[Route]) -> Metrics
world.apply_disruption(event: DisruptionEvent) -> WorldState
```

`WorldState`, `DeliveryRequest`, `Route`, `Metrics`, `DisruptionEvent` are pydantic models in `src/sim/models.py` so they're trivially JSON-serializable for tool calls.

### 2.2 Tools (`src/tools/`) — owned jointly
Thin CrewAI tool wrappers. One file per tool. Each tool calls into `src/sim/` and returns a string or a small dict.

Initial tool set:
- `read_world_state` — returns `WorldState` as JSON
- `propose_routes` — accepts a list of routes, returns `Metrics`
- `inject_disruption` — for the Disruption Agent's testing
- (later) `web_search` if any agent needs external context

### 2.3 Agents (`src/agents/`) — Person A
One file per agent. Each agent is a CrewAI `Agent` with role/goal/backstory + a tool list + an LLM from `src/llm.py`.

| Agent | Input | Output | Tools |
|---|---|---|---|
| **Demand** | world snapshot | list of `DeliveryRequest` | `read_world_state` |
| **Routing** | demand list, world snapshot | initial `list[Route]` | `read_world_state`, `propose_routes` |
| **Efficiency** | initial routes, metrics | optimized `list[Route]` | `propose_routes` |
| **Disruption** | optimized routes, disruption event | rerouted `list[Route]` | `read_world_state`, `propose_routes` |

The agents run sequentially in `main.py`. Cross-agent communication goes through CrewAI task outputs, not shared globals.

### 2.4 Tasks (`src/tasks/`) — Person A
One CrewAI `Task` per agent stage. Tasks define the prompt-level instructions and the expected output schema. Outputs are validated via pydantic.

### 2.5 LLM client (`src/llm.py`) — Person A
A single factory `amd_llm(model=None, temperature=None) -> LLM` that returns a CrewAI `LLM` (or a LangChain `ChatOpenAI`, depending on what plays nicer with CrewAI's tool-calling). Reads `AMD_API_BASE_URL`, `AMD_API_KEY`, `MODEL_NAME` from env. **All agents import from here.**

### 2.6 Dashboard (`dashboard/`) — Person C
Streamlit app. Reads run output from a known location (proposed: `output/last_run.json` written by `main.py`). Renders:
- the grid + nodes + current routes
- metrics panel (distance, time, energy, % improvement)
- a "Trigger disruption" button that re-runs the crew with a new event

Real-time updates can be polling-based (Streamlit auto-rerun). Don't over-engineer with websockets in v1.

---

## 3. Data flow (one demo run)

1. `main.py` builds a `World` with a fixed seed.
2. `main.py` writes the initial state to `output/last_run.json` so the dashboard can render the "before" view.
3. CrewAI kicks off the four-agent sequence:
   - Demand Agent surveys the world → produces `DeliveryRequest`s.
   - Routing Agent assigns deliveries to initial routes.
   - Efficiency Agent rewrites routes for shorter/cheaper/faster.
   - Disruption Agent (when triggered) reroutes around the event.
4. After each stage, the route + metrics are appended to `output/last_run.json`.
5. The dashboard polls and re-renders.

---

## 4. AMD / LLM integration

- AMD Developer Cloud exposes an OpenAI-compatible HTTP endpoint per deployed model.
- We use the `openai` Python SDK (or CrewAI's wrapper) with `base_url=AMD_API_BASE_URL` and `api_key=AMD_API_KEY`.
- Default dev model: an 8B model (Llama-3-8B-Instruct or Mistral-7B-Instruct). Cheap, fast, good enough for iteration.
- Final demo can be a larger model if budget allows.
- All LLM calls go through `src/llm.py`. This is the single place to flip models, add tracing, or add a cache.

---

## 5. Open decisions

These need a team call before we build past v0:

- [ ] **Which 8B model do we standardize on for dev?** Llama-3-8B-Instruct vs Mistral-7B-Instruct. Pick one so caching works.
- [ ] **How does the Disruption Agent get triggered in the demo?** Dashboard button → re-runs full crew, or → only re-runs Disruption Agent? Affects latency.
- [ ] **Do we need a persistent run log** (jsonl per run) or is overwriting `output/last_run.json` enough for the demo?
- [ ] **Eval harness:** do we ship one, or do we eyeball it on a fixed seeded scenario? Recommendation: fixed scenario + a small `tests/test_demo_scenario.py` that asserts metrics improved.

---

## 6. What's intentionally not in v1

- Multi-depot routing.
- Vehicle capacity constraints.
- Time windows for deliveries.
- A real map / OSM data — the 2D grid is the world.
- Database persistence — `output/last_run.json` is the only state.

These are reasonable v2 ideas if we have time after May 9. Don't pre-build for them.
