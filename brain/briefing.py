"""
Daily Briefing Engine.

Generates morning and evening briefings by synthesizing signals
surfaced by Hermes, plus business metrics, into actionable updates
for Jim. Uses Claude API with prompt templates from config/prompts.yaml.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from brain.client import get_client, get_model, extract_text
from brain.models import (
    BriefingSection,
    BriefingType,
    BusinessMetric,
    DailyBriefing,
    HermesDigest,
    HermesSignal,
    MetricsSnapshot,
    Priority,
)

# Load prompt templates
_PROMPTS_PATH = Path("config/prompts.yaml")


def _load_prompts() -> dict:
    if _PROMPTS_PATH.exists():
        return yaml.safe_load(_PROMPTS_PATH.read_text(encoding="utf-8")) or {}
    return {}


def _format_signals(signals: list[HermesSignal]) -> str:
    """Format signals into a readable text block for the prompt."""
    if not signals:
        return "No new signals in this window."

    lines = []
    for s in signals:
        source_label = s.source.value.upper()
        priority_label = f"[{s.priority.value.upper()}]"
        lines.append(f"- {source_label} {priority_label}: {s.title}")
        lines.append(f"  Summary: {s.summary}")
        if s.requires_response:
            lines.append(f"  ⚠ REQUIRES RESPONSE from {s.sender or 'unknown'}")
        lines.append(f"  Full text: {s.raw_text[:500]}")
        lines.append("")
    return "\n".join(lines)


def _format_metrics(metrics: list[BusinessMetric]) -> str:
    """Format metrics into a readable block."""
    if not metrics:
        return "No metrics available."
    lines = []
    for m in metrics:
        trend = f" (trend: {m.trend})" if m.trend else ""
        prev = f" (prev: {m.previous_value}{m.unit})" if m.previous_value is not None else ""
        lines.append(f"- {m.name}: {m.value}{m.unit}{prev}{trend}")
        if m.note:
            lines.append(f"  Note: {m.note}")
    return "\n".join(lines)


def generate_briefing(
    digest: HermesDigest,
    metrics: MetricsSnapshot | None = None,
    briefing_type: BriefingType = BriefingType.MORNING,
    morning_context: str = "",
    date: datetime | None = None,
) -> DailyBriefing:
    """
    Generate a daily briefing from Hermes signals and metrics.

    Args:
        digest: The Hermes digest containing surfaced signals
        metrics: Optional metrics snapshot
        briefing_type: morning or evening
        morning_context: For evening briefings, what was in the morning briefing
        date: Override date (defaults to now)

    Returns:
        DailyBriefing with structured sections
    """
    client = get_client()
    model = get_model()
    prompts = _load_prompts()
    date = date or datetime.utcnow()

    metrics_list = metrics.metrics if metrics else []
    time_window = f"{digest.time_window_start} to {digest.time_window_end}"

    if briefing_type == BriefingType.MORNING:
        prompt_template = prompts.get("morning_briefing", "")
        prompt = prompt_template.format(
            date=date.strftime("%A, %B %d, %Y"),
            time_window=time_window,
            signals=_format_signals(digest.signals),
            metrics=_format_metrics(metrics_list),
        )
    else:
        prompt_template = prompts.get("evening_briefing", "")
        prompt = prompt_template.format(
            date=date.strftime("%A, %B %d, %Y"),
            morning_context=morning_context or "No morning briefing was generated.",
            signals=_format_signals(digest.signals),
            metrics=_format_metrics(metrics_list),
        )

    from brain.learning import lessons_block
    system = (
        "You are the Operations Co-Founder for Jim Harshaw Jr.'s coaching "
        "business. You produce concise, actionable daily briefings. Be "
        "direct. No fluff. Jim is a former D1 wrestling coach."
    ) + lessons_block("briefing")

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = extract_text(response)

    # Parse the structured response into sections
    sections = _parse_briefing_sections(raw_text)
    headline = sections[0].content if sections else ""
    requires_attention = _extract_requires_jim(raw_text)

    return DailyBriefing(
        briefing_type=briefing_type,
        date=date,
        headline=headline,
        sections=sections[1:] if len(sections) > 1 else sections,  # rest after headline
        key_metrics=metrics_list,
        requires_jim_attention=requires_attention,
    )


def _parse_briefing_sections(text: str) -> list[BriefingSection]:
    """Parse numbered sections from the briefing output."""
    sections = []
    current_heading = ""
    current_content: list[str] = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect section headers like "1. HEADLINE" or "HEADLINE"
        if line[0].isdigit() and ". " in line[:4]:
            if current_heading:
                sections.append(BriefingSection(
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                ))
            parts = line.split(". ", 1)
            current_heading = parts[1] if len(parts) > 1 else line
            current_content = []
        elif line.upper() == line and len(line) < 60 and not line.endswith("."):
            # All-caps short line is likely a section header
            if current_heading and current_content:
                sections.append(BriefingSection(
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                ))
            current_heading = line
            current_content = []
        else:
            current_content.append(line)

    if current_heading:
        sections.append(BriefingSection(
            heading=current_heading,
            content="\n".join(current_content).strip(),
        ))

    if not sections:
        # Fallback: treat whole text as one section
        sections.append(BriefingSection(heading="BRIEFING", content=text))

    return sections


def _extract_requires_jim(text: str) -> list[str]:
    """Extract items from the REQUIRES JIM section."""
    items = []
    in_section = False
    for line in text.split("\n"):
        stripped = line.strip()
        if "REQUIRES JIM" in stripped.upper():
            in_section = True
            continue
        if in_section:
            if stripped and (stripped[0].isdigit() or stripped.startswith("-")):
                items.append(stripped.lstrip("0123456789.-) ").strip())
            elif stripped and stripped.isupper() and len(stripped) < 50:
                break  # next section
            elif stripped and in_section:
                pass  # continuation line
    return items
