# AI agents for delivery logistics optimization (project name tbd)

## Overview
LogistiAI is a multi-agent AI system that simulates and optimizes delivery logistics in real time.

The system uses multiple collaborating AI agents, each responsible for a different part of the logistics pipeline:
- Demand planning
- Route generation
- Efficiency optimization
- Real-time disruption handling

The goal is to demonstrate how agentic AI systems can coordinate to solve complex real-world logistics problems.

---

## AI Agents

### Demand Agent
- Determines what needs to be shipped
- Generates delivery requests

### Routing Agent
- Assigns deliveries to routes
- Creates initial path planning

### Efficiency Agent
- Optimizes routes for:
  - shortest distance
  - lowest energy usage
  - fastest delivery time

### Disruption Agent
- Handles real-time events:
  - traffic
  - road closures
  - delays
- Dynamically updates routes

---

## Simulation
- Simple 2D grid map
- 1 depot (start point)
- 10–30 delivery nodes
- Optional blocked nodes (disruptions)

---

## Tech Stack
- Python (backend + agents)
- CrewAI (multi-agent framework)
- Streamlit (frontend dashboard)
- Llama / Mistral (LLMs via AMD cloud)
- GitHub (collaboration)

---

## Demo Flow
1. Show initial inefficient delivery routes
2. Activate AI agent system
3. Show optimized routes
4. Introduce disruption
5. Show real-time rerouting
6. Display performance improvements

---

## Metrics
- Total distance traveled
- Estimated delivery time
- Energy/fuel usage
- Improvement percentage

---

## Team Roles

### Person A — AI & Agents
- CrewAI system
- LLM integration (AMD cloud)
- Agent communication logic

### Person B — Backend & Simulation
- Grid system
- Routing logic
- Metrics calculation
- Disruption engine

### Person C — Frontend & Demo
- Streamlit dashboard
- Visualization (routes, nodes)
- Demo flow + UI polish

---

## Workflow
All work is done on feature branches → merged into `dev` → stable versions go to `main`.