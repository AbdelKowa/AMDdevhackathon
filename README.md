# AMDdevhackathon

> lablab.ai AMD Developer Hackathon — May 4–10, 2026
> Track 1: AI Agents & Agentic Workflows

## Team
- [AbdelKowa](https://github.com/AbdelKowa)
- *(teammates — add yourselves)*

## Project
TBD — decided on May 4.

## Tech Stack
- **Framework:** CrewAI
- **Models:** Open-source (Llama 3 / DeepSeek / Mistral / Qwen) via AMD Developer Cloud
- **Compute:** $100 AMD Developer Cloud credits

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/AbdelKowa/AMDdevhackathon.git
cd AMDdevhackathon
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your AMD API key and settings
```

### 5. Run
```bash
# TBD once project idea is locked
python src/main.py
```

## Project Structure
```
AMDdevhackathon/
├── src/
│   ├── agents/       # CrewAI agent definitions
│   ├── tasks/        # CrewAI task definitions
│   ├── tools/        # Custom tools for agents
│   └── main.py       # Entry point
├── notebooks/        # Exploration & prototyping
├── docs/             # Architecture diagrams, notes
├── tests/            # Unit tests
├── .env.example      # Environment variable template
├── requirements.txt
└── README.md
```

## Branch Strategy
- `main` — stable, demo-ready code only
- `dev` — integration branch, merge features here first
- `feature/<name>` — individual feature branches

## Contributing
1. Branch off `dev`: `git checkout -b feature/your-feature dev`
2. Commit your work
3. Open a PR into `dev`
4. `dev` → `main` only for stable milestones
