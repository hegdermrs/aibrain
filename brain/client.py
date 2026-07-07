"""
Shared Anthropic client factory for the Brain.
"""

from __future__ import annotations

import os
from functools import lru_cache

from anthropic import Anthropic


@lru_cache()
def get_client() -> Anthropic:
    """Return a cached Anthropic client instance."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Create a .env file or export it."
        )
    return Anthropic(api_key=api_key)


def get_model() -> str:
    """Return the model name from env or default."""
    return os.environ.get("BRAIN_MODEL", "claude-sonnet-4-20250514")
