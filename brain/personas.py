"""
Persona System — Configurable strategic thinking personas.

Personas pressure-test decisions through different lenses:
- Hormozi: offers, value, growth, pricing
- Musk: first principles, physics thinking, engineering
- More to come as needed.

Personas are defined in config/personas.yaml and loaded at runtime.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from brain.models import PersonaConfig, PersonaResponse

# Default persona config path, override with env var
import os
DEFAULT_CONFIG_PATH = Path(
    os.environ.get("BRAIN_PERSONAS_CONFIG", "config/personas.yaml")
)


class PersonaRegistry:
    """Loads and manages the set of available personas."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = Path(config_path or DEFAULT_CONFIG_PATH)
        self._personas: dict[str, PersonaConfig] = {}
        self._load()

    def _load(self) -> None:
        """Load personas from YAML config."""
        if not self.config_path.exists():
            self._load_builtins()
            return
        raw = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
        if not raw or "personas" not in raw:
            self._load_builtins()
            return
        for p in raw["personas"]:
            persona = PersonaConfig(**p)
            self._personas[persona.name.lower()] = persona

    def _load_builtins(self) -> None:
        """Hardcoded fallback personas if config is missing."""
        self._personas = {
            "hormozi": PersonaConfig(
                name="Hormozi",
                tagline="Value, offers, and growth — Alex Hormozi style",
                description=(
                    "You are Alex Hormozi, entrepreneur and growth expert. "
                    "You think in terms of irresistible offers, value delivery, "
                    "pricing leverage, and scalable growth engines. You believe "
                    "most business problems are offer problems in disguise."
                ),
                thinking_style=(
                    "Cut to the value equation. What is the dream outcome, "
                    "perceived likelihood of achievement, time delay, and "
                    "effort/sacrifice? Where is the bottleneck in the value "
                    "delivery chain? Can we make the offer so good people "
                    "feel stupid saying no?"
                ),
                key_questions=[
                    "What is the value equation here?",
                    "Is this an offer problem or a traffic problem?",
                    "Where is the bottleneck?",
                    "Can we increase perceived value 10x?",
                ],
                biases=[
                    "Sees everything through offer and value lens",
                    "Assumes growth constraints are internal, not market",
                    "Prefers pricing up over cost cutting",
                ],
            ),
            "musk": PersonaConfig(
                name="Musk",
                tagline="First principles and physics thinking — Elon Musk style",
                description=(
                    "You are Elon Musk, engineer and first-principles thinker. "
                    "You strip problems down to their most fundamental truths "
                    "and reason up from there. You reject reasoning by analogy "
                    "and demand that constraints be proven, not assumed."
                ),
                thinking_style=(
                    "Boil it down to the most fundamental truths. What are we "
                    "certain is true? What are we assuming? What would the "
                    "simplest possible version of this look like? Is the "
                    "constraint real or just 'how it's always been done'?"
                ),
                key_questions=[
                    "What are the first principles here?",
                    "Which constraints are real vs. assumed?",
                    "What is the simplest possible version?",
                    "If we had to do this 10x cheaper/faster, how would we?",
                ],
                biases=[
                    "Dismisses institutional inertia as invalid",
                    "Overestimates ability to reinvent from scratch",
                    "Underweights social/human friction vs. technical",
                ],
            ),
        }

    def list(self) -> list[str]:
        """List available persona names."""
        return list(self._personas.keys())

    def get(self, name: str) -> Optional[PersonaConfig]:
        """Get a persona by name (case-insensitive)."""
        return self._personas.get(name.lower())

    def get_all(self) -> list[PersonaConfig]:
        """Get all loaded personas."""
        return list(self._personas.values())

    def system_prompt_for(self, name: str) -> str:
        """Build a system prompt for a given persona."""
        p = self.get(name)
        if p is None:
            raise ValueError(f"Unknown persona: {name}")
        return (
            f"{p.description}\n\n"
            f"Thinking style: {p.thinking_style}\n\n"
            f"Key questions you always ask:\n"
            + "\n".join(f"- {q}" for q in p.key_questions)
            + f"\n\nKnown biases (be aware of):\n"
            + "\n".join(f"- {b}" for b in p.biases)
        )


# Singleton — personas shouldn't change mid-run but YAML can be reloaded
_registry: Optional[PersonaRegistry] = None


def get_registry() -> PersonaRegistry:
    global _registry
    if _registry is None:
        _registry = PersonaRegistry()
    return _registry


def reload_registry() -> PersonaRegistry:
    global _registry
    _registry = PersonaRegistry()
    return _registry
