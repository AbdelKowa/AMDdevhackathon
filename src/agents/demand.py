"""Demand Agent — surveys the world and decides what needs to ship."""
from __future__ import annotations

from crewai import Agent

from src.llm import amd_llm

# TODO(Person A/B): import once src/tools/ exists.
# from src.tools.read_world_state import read_world_state

demand_agent = Agent(
    role="Delivery Demand Planner",
    goal=(
        "Inspect the current world snapshot and produce a clean, deduplicated "
        "list of DeliveryRequests for today's run. Do not invent nodes that "
        "are not present in the snapshot."
    ),
    backstory=(
        "You are a senior logistics dispatcher. You have spent years deciding "
        "which orders go out on which day. You are conservative: you only "
        "schedule deliveries to nodes the simulation reports as active and "
        "reachable, and you never duplicate a request."
    ),
    tools=[
        # read_world_state,
    ],
    llm=amd_llm(),
    allow_delegation=False,
    verbose=True,
)
