# CLAUDE.md

## Project
lablab.ai AMD Developer Hackathon — Track 1: AI Agents & Agentic Workflows (May 4–10, 2026).
Team of 4 building a multi-agent AI system using CrewAI + open-source LLMs on AMD Developer Cloud.

## Stack
- **CrewAI** for agent orchestration
- **Open-source models** (Llama 3, DeepSeek, Mistral, or Qwen) hosted on AMD cloud
- AMD models are accessed via an **OpenAI-compatible API** — use the `openai` Python client pointed at the AMD base URL
- Python 3.11+, virtual env at `.venv/`

## Structure
- `src/agents/` — CrewAI Agent definitions (role, goal, backstory, tools)
- `src/tasks/` — CrewAI Task definitions
- `src/tools/` — Custom tools agents can call
- `src/main.py` — Crew assembly and kickoff
- `notebooks/` — Scratch exploration, not production code
- `docs/` — Architecture notes and diagrams

## Environment
All secrets live in `.env` (never committed). See `.env.example` for required keys.
Load with `python-dotenv`: `from dotenv import load_dotenv; load_dotenv()`.

## Branch Strategy
- `main` — demo-ready only
- `dev` — integration branch
- `feature/<name>` — individual work, PR into `dev`

## Key Constraints
- Stay within $100 AMD compute budget — prefer smaller models (8B) for iteration, scale up only for final demo
- No proprietary model APIs (OpenAI, Anthropic, etc.) — AMD track requires open-source models on AMD hardware
