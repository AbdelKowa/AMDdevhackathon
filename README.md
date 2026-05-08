# AI Agents for Delivery Logistics Optimization

> *Project name: TBD* — a multi-agent AI system that simulates and optimizes delivery logistics in real time.
> Built for the **lablab.ai AMD Developer Hackathon — Track 1: AI Agents & Agentic Workflows** (May 4–10, 2026).

Four cooperating CrewAI agents — **Demand**, **Routing**, **Efficiency**, **Disruption** — plan deliveries on a 2D grid, optimize the routes, and react to live disruptions like road closures and traffic. A Streamlit dashboard visualizes the before/after and lets the audience trigger disruptions on the fly.

- **Concept & demo flow:** [`project-overview.md`](project-overview.md)
- **Architecture & contracts:** [`docs/architecture.md`](docs/architecture.md)

## Team & Ownership

Three people. Stay inside your area unless you've coordinated with the owner.

| Owner | Area | Primary files |
|---|---|---|
| [AbdelKowa](https://github.com/AbdelKowa) — Person A | AI & Agents (4 agents + LLM glue) | `src/agents/`, `src/tasks/`, `src/llm.py`, `src/main.py` |
| [Nate1396](https://github.com/Nate1396) — Person B | Backend & Simulation | `src/sim/`, `src/tools/` |
| *teammate* — Person C | Frontend & Demo | `dashboard/`, demo script |

The contract between Person A and Person B is the simulation API in `src/sim/` — agents call it through `src/tools/`, they don't reach into sim internals. See [`docs/architecture.md`](docs/architecture.md).

## Tech Stack
- **Framework:** CrewAI
- **Models:** open-source (Llama 3 / Mistral) via AMD Developer Cloud (OpenAI-compatible API)
- **Frontend:** Streamlit
- **Compute:** $100 AMD Developer Cloud credits

## Setup

### 1. Clone
```bash
git clone https://github.com/AbdelKowa/AMDdevhackathon.git
cd AMDdevhackathon
```

### 2. Virtual env
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
```

### 3. Install
```bash
pip install -r requirements.txt
```

### 4. Environment
```bash
cp .env.example .env
# fill in AMD_API_KEY and AMD_API_BASE_URL
```

### 5. Run the crew
```bash
python -m src.main
```

### 6. Run the dashboard
```bash
streamlit run dashboard/app.py
```

## Project Structure
```
AMDdevhackathon/
├── src/
│   ├── agents/       # CrewAI agent definitions (Person A)
│   ├── tasks/        # CrewAI task definitions (Person A)
│   ├── tools/        # Custom tools agents call (wrap sim API)
│   ├── sim/          # Grid + routing + metrics + disruption engine (Person B)
│   ├── llm.py        # AMD LLM client factory — import from here
│   └── main.py       # Crew assembly + entry point
├── dashboard/        # Streamlit UI (Person C)
├── notebooks/        # Scratch exploration
├── docs/             # Architecture notes
├── tests/            # Pytest
├── output/           # Run artifacts (gitignored)
├── .env.example
├── requirements.txt
├── project-overview.md
├── CLAUDE.md         # Working notes for Claude Code
└── README.md
```

## Contributing

### Branching
- `main` — demo-ready only. Don't push directly.
- `dev` — integration branch. Merge `feature/*` here.
- `feature/<owner>-<scope>` — e.g. `feature/abdel-demand-agent`. PR into `dev`.

### Commits
- Short imperative subject lines: `add demand agent stub`, not `Added the demand agent stub`.
- Group commits by logical unit. Squash-merge into `dev` to keep history readable.

### Pull requests
- Open against `dev` (never `main`).
- Description: what changed, why, anything reviewers should test manually.
- Run `pytest` locally before opening the PR.
- Don't `--no-verify` or skip CI hooks. If something fails, fix the root cause.

### Daily integration
End-of-day: merge your feature branch into `dev` (or open a PR for review) so the others can pull a working state in the morning. Don't sit on a branch for multiple days.

### Ownership boundaries
If you need a change in someone else's area, ask in the team chat or open a PR with a clear ask — don't silently edit across boundaries. Person A's agents talk to Person B's simulation through `src/tools/` only.

### Cost discipline ($100 budget)
- **Default to 8B models** (Llama-3-8B / Mistral-7B) for development. Switch to a larger model only for the final demo run.
- CrewAI caching is on by default — keep it on so re-running the same crew over the same inputs doesn't re-call the API.
- Don't run the full crew in a tight loop while debugging a single agent.
- **Watch the AMD usage dashboard daily.** If we burn through >$50 by May 8, scale back.

### Don't commit
- `.env` or any secrets. `.gitignore` covers it; double-check `git status` before committing.
- Model weights or large artifacts.
- Proprietary model API calls (OpenAI, Anthropic, etc.) for inference. The AMD track requires open-source models on AMD hardware. The `openai` package is allowed only as a *client library* pointed at the AMD endpoint.

### Demo timeline (today is May 5, demo May 10)
- **May 5 (Tue):** scaffold each agent stub, AMD client smoke test, grid sim skeleton, dashboard placeholder.
- **May 6 (Wed):** every agent returns *something* end-to-end on a hardcoded scenario. Streamlit shows a static map.
- **May 7 (Thu):** efficiency + disruption integrated. Real metrics flowing to the dashboard.
- **May 8 (Fri):** polish, eval pass, write the demo script.
- **May 9 (Sat):** rehearsal. Lock the demo scenario. Final-model run on AMD.
- **May 10 (Sun):** submission.

If a day's milestone slips, cut scope on the demo, not on time — the deadline is fixed.

## License
TBD — pick one before submission.
