"""Test-suite fixtures and env defaults.

Importing any agent or task constructs an LLM via `amd_llm()`, which reads
AMD_API_KEY / AMD_API_BASE_URL / MODEL_NAME from the environment. Set
harmless fallbacks so the import-only tests work in CI without secrets.
No network call is made at import time, so bogus values are safe.
"""
from __future__ import annotations

import os

_DEFAULTS = {
    "AMD_API_KEY": "test-key",
    "AMD_API_BASE_URL": "https://example.invalid/v1",
    "MODEL_NAME": "meta-llama/Llama-3-8b-instruct",
    "MODEL_TEMPERATURE": "0.7",
}

for key, value in _DEFAULTS.items():
    os.environ.setdefault(key, value)
