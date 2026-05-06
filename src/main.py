"""Crew entry point.

Wires the four agents (Demand, Routing, Efficiency, Disruption) into a
sequential CrewAI pipeline over a seeded grid world, then writes the run
artifacts to output/last_run.json for the Streamlit dashboard to read.
"""
from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

# TODO(Person A): wire these in as agents/tasks land
# from crewai import Crew, Process
# from src.agents.demand import demand_agent
# from src.agents.routing import routing_agent
# from src.agents.efficiency import efficiency_agent
# from src.agents.disruption import disruption_agent
# from src.tasks.demand import demand_task
# from src.tasks.routing import routing_task
# from src.tasks.efficiency import efficiency_task
# from src.tasks.disruption import disruption_task

# TODO(Person B): expose World + a seeded scenario factory
# from src.sim import World


def run() -> None:
    # world = World(seed=42, n_nodes=20)
    # crew = Crew(
    #     agents=[demand_agent, routing_agent, efficiency_agent, disruption_agent],
    #     tasks=[demand_task, routing_task, efficiency_task, disruption_task],
    #     process=Process.sequential,
    #     verbose=True,
    # )
    # result = crew.kickoff(inputs={"world": world.snapshot()})
    # write_run_artifact(result)
    print("Crew not yet wired — see TODOs in src/main.py")


if __name__ == "__main__":
    run()
