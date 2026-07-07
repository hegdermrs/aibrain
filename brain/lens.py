"""
Strategic Lens — Pressure-test decisions through configurable personas.

Takes a question or decision, runs it through selected personas
(e.g. Hormozi for offers/growth, Musk for first-principles), and
synthesizes the results into actionable advice for Jim.

Uses Claude API with persona system prompts and the lens templates.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from brain.client import get_client, get_model, extract_text
from brain.models import LensQuery, LensResult, PersonaResponse
from brain.personas import get_registry

_PROMPTS_PATH = Path("config/prompts.yaml")


def _load_prompts() -> dict:
    if _PROMPTS_PATH.exists():
        return yaml.safe_load(_PROMPTS_PATH.read_text(encoding="utf-8")) or {}
    return {}


def run_lens(query: LensQuery) -> LensResult:
    """
    Pressure-test a decision through selected strategic personas.

    Args:
        query: The question/decision with context and selected personas.
               If personas list is empty, uses all available personas.

    Returns:
        LensResult with per-persona analysis and cross-persona synthesis
    """
    registry = get_registry()
    prompts = _load_prompts()

    # Determine which personas to use
    persona_names = query.personas if query.personas else registry.list()
    persona_configs = []
    for name in persona_names:
        cfg = registry.get(name)
        if cfg:
            persona_configs.append(cfg)

    if not persona_configs:
        raise ValueError("No valid personas found. Check config/personas.yaml")

    # Get responses from each persona
    responses: list[PersonaResponse] = []
    for persona in persona_configs:
        response = _ask_persona(persona, query, prompts)
        responses.append(response)

    # Synthesize cross-persona analysis
    synthesis = _synthesize(query, responses, prompts)

    return LensResult(
        query=query,
        persona_responses=responses,
        synthesis=synthesis,
    )


def run_lens_parallel(query: LensQuery) -> LensResult:
    """
    Same as run_lens but queries personas concurrently.
    Use when latency matters and you have multiple personas.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    registry = get_registry()
    prompts = _load_prompts()

    persona_names = query.personas if query.personas else registry.list()
    persona_configs = []
    for name in persona_names:
        cfg = registry.get(name)
        if cfg:
            persona_configs.append(cfg)

    if not persona_configs:
        raise ValueError("No valid personas found. Check config/personas.yaml")

    responses: list[PersonaResponse] = []
    with ThreadPoolExecutor(max_workers=len(persona_configs)) as executor:
        futures = {
            executor.submit(_ask_persona, p, query, prompts): p
            for p in persona_configs
        }
        for future in as_completed(futures):
            responses.append(future.result())

    # Maintain order
    name_order = {p.name: i for i, p in enumerate(persona_configs)}
    responses.sort(key=lambda r: name_order.get(r.persona_name, 999))

    synthesis = _synthesize(query, responses, prompts)

    return LensResult(
        query=query,
        persona_responses=responses,
        synthesis=synthesis,
    )


def _ask_persona(persona, query: LensQuery, prompts: dict) -> PersonaResponse:
    """Ask a single persona for their analysis."""
    from brain.personas import get_registry

    client = get_client()
    model = get_model()
    registry = get_registry()

    template = prompts.get("lens_persona_prompt", "")
    constraints = "\n".join(f"- {c}" for c in query.constraints) if query.constraints else "None specified."

    prompt = template.format(
        persona_prompt=registry.system_prompt_for(persona.name),
        question=query.question,
        context=query.context or "No additional context provided.",
        constraints=constraints,
    )

    from brain.learning import lessons_block
    response = client.messages.create(
        model=model,
        max_tokens=1536,
        system=registry.system_prompt_for(persona.name) + lessons_block("lens"),
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = extract_text(response)

    # Extract key insight and recommended action
    key_insight = ""
    recommended_action = ""

    for line in raw_text.split("\n"):
        stripped = line.strip()
        if ("key insight" in stripped.lower() or "blind spot" in stripped.lower()) and not key_insight:
            key_insight = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
        if "recommend" in stripped.lower() and not recommended_action:
            recommended_action = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped

    return PersonaResponse(
        persona_name=persona.name,
        analysis=raw_text,
        key_insight=key_insight or raw_text[:200],
        recommended_action=recommended_action or "See full analysis.",
    )


def _synthesize(query: LensQuery, responses: list[PersonaResponse], prompts: dict) -> str:
    """Synthesize multiple persona responses into a coherent recommendation."""
    client = get_client()
    model = get_model()

    template = prompts.get("lens_synthesis", "")

    responses_text = ""
    for i, r in enumerate(responses, 1):
        responses_text += f"\n--- {r.persona_name} ---\n{r.analysis}\n"

    prompt = template.format(
        question=query.question,
        context=query.context or "No additional context.",
        responses=responses_text,
    )

    from brain.learning import lessons_block
    response = client.messages.create(
        model=model,
        max_tokens=1536,
        system=(
            "You are the Operations Co-Founder for Jim Harshaw Jr.'s coaching "
            "business. You synthesize strategic advice from multiple perspectives. "
            "Be honest about disagreements — Jim needs to see tensions, not "
            "artificial harmony."
        ) + lessons_block("lens"),
        messages=[{"role": "user", "content": prompt}],
    )

    return extract_text(response)
