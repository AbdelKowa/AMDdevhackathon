"""AMD LLM client factory.

All agents must build their LLM through `amd_llm()` so we have a single
place to flip models, swap endpoints, or add tracing. Do not instantiate
OpenAI / CrewAI LLM clients inline elsewhere in the codebase.
"""
from __future__ import annotations

import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def amd_llm(model: str | None = None, temperature: float | None = None) -> LLM:
    """Return a CrewAI LLM pointed at the AMD Developer Cloud endpoint.

    AMD exposes an OpenAI-compatible API per deployed model, so we route
    through litellm's `openai/` provider prefix.
    """
    resolved_model = model or os.environ["MODEL_NAME"]
    resolved_temp = (
        temperature
        if temperature is not None
        else float(os.environ.get("MODEL_TEMPERATURE", "0.7"))
    )
    return LLM(
        model=f"openai/{resolved_model}",
        base_url=os.environ["AMD_API_BASE_URL"],
        api_key=os.environ["AMD_API_KEY"],
        temperature=resolved_temp,
    )
