"""
Call Transcript Analyzer.

Ingests call transcripts (from Fathom/Zoom/Meet via Hermes) and surfaces:
- Decisions made
- Follow-up items with owners
- Delegation and automation candidates
- Key themes and patterns

Uses Claude API with prompt templates from config/prompts.yaml.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from brain.client import get_client, get_model
from brain.models import (
    AutomationCandidate,
    CallAnalysis,
    CallTranscript,
    Decision,
    DecisionStatus,
    FollowUp,
    Priority,
)

_PROMPTS_PATH = Path("config/prompts.yaml")


def _load_prompts() -> dict:
    if _PROMPTS_PATH.exists():
        return yaml.safe_load(_PROMPTS_PATH.read_text(encoding="utf-8")) or {}
    return {}


def analyze_transcript(transcript: CallTranscript) -> CallAnalysis:
    """
    Analyze a call transcript and surface decisions, follow-ups,
    and delegation/automation opportunities.

    Args:
        transcript: The call transcript to analyze

    Returns:
        CallAnalysis with structured findings
    """
    client = get_client()
    model = get_model()
    prompts = _load_prompts()

    prompt_template = prompts.get("call_analysis", "")
    prompt = prompt_template.format(
        call_title=transcript.title,
        date=transcript.date.strftime("%A, %B %d, %Y"),
        participants=", ".join(transcript.participants),
        duration=f"{transcript.duration_minutes:.0f}",
        transcript=transcript.full_text,
    )

    from brain.learning import lessons_block
    system = (
        "You are the Operations Co-Founder for Jim Harshaw Jr.'s coaching "
        "business. You analyze call transcripts to surface decisions, "
        "follow-ups, and what should be delegated or automated. "
        "Be precise and thorough — missed follow-ups are the most "
        "expensive failure mode."
    ) + lessons_block("analysis")

    response = client.messages.create(
        model=model,
        max_tokens=3072,
        temperature=0.5,  # lower temp for more factual extraction
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text

    # Parse structured output
    summary = _extract_section(raw_text, "SUMMARY")
    decisions = _parse_decisions(raw_text)
    follow_ups = _parse_follow_ups(raw_text)
    automation = _parse_automation(raw_text)
    themes = _parse_key_themes(raw_text)

    return CallAnalysis(
        call_id=transcript.id,
        call_title=transcript.title,
        summary=summary,
        decisions=decisions,
        follow_ups=follow_ups,
        automation_candidates=automation,
        key_themes=themes,
    )


def analyze_latest(transcript_dir: str = "./data/transcripts") -> CallAnalysis | None:
    """
    Convenience: analyze the most recent transcript in the directory.
    Returns None if no transcripts found.
    """
    from brain.hermes_interface import HermesInterface
    hermes = HermesInterface(transcript_dir=transcript_dir)
    transcript = hermes.read_latest_transcript()
    if transcript is None:
        return None
    return analyze_transcript(transcript)


# ── Parsing helpers ──────────────────────────────────────────────────────────


def _extract_section(text: str, section_name: str) -> str:
    """Extract the content of a named section from the response text."""
    in_section = False
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if section_name.upper() in stripped.upper() and (
            stripped[0].isdigit() or stripped.upper().startswith(section_name.upper())
        ):
            in_section = True
            # If the section header contains content after a colon/hyphen
            if ":" in stripped:
                after = stripped.split(":", 1)[1].strip()
                if after:
                    lines.append(after)
            continue
        if in_section:
            # Check if we've hit the next numbered section
            if stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                break
            if stripped:
                lines.append(stripped)
    return "\n".join(lines).strip()


def _parse_decisions(text: str) -> list[Decision]:
    """Parse decisions from the DECISIONS section."""
    section_text = _extract_section(text, "DECISIONS")
    if not section_text:
        return []

    decisions = []
    current_desc: list[str] = []
    current_made_by = "Jim"

    for line in section_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") or (stripped[0].isdigit() and "." in stripped[:3]):
            # Save previous
            if current_desc:
                desc = " ".join(current_desc).strip()
                decisions.append(Decision(
                    description=desc,
                    made_by=current_made_by,
                ))
            # Start new
            clean = stripped.lstrip("-0123456789.) ").strip()
            current_desc = [clean]
            current_made_by = "Jim"
        elif "made by" in stripped.lower() or "decided by" in stripped.lower():
            current_made_by = stripped.split("by", 1)[-1].strip().rstrip(".")
            decisions.append(Decision(
                description=" ".join(current_desc).strip(),
                made_by=current_made_by,
            ))
            current_desc = []
        else:
            current_desc.append(stripped)

    # Don't miss the last one
    if current_desc:
        desc = " ".join(current_desc).strip()
        if desc:
            decisions.append(Decision(description=desc, made_by=current_made_by))

    return decisions


def _parse_follow_ups(text: str) -> list[FollowUp]:
    """Parse follow-up items from the FOLLOW-UPS section."""
    section_text = _extract_section(text, "FOLLOW-UPS")
    if not section_text:
        return []

    follow_ups = []
    for line in section_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") or (stripped[0].isdigit() and "." in stripped[:3]):
            clean = stripped.lstrip("-0123456789.) ").strip()
            owner = "Jim"
            priority = Priority.MEDIUM
            if "owner:" in clean.lower():
                parts = clean.split("owner:", 1)
                clean = parts[0].strip()
                owner_part = parts[1].strip()
                owner = owner_part.split(",")[0].strip()
            if "[" in clean and "]" in clean:
                bracket = clean[clean.index("[")+1:clean.index("]")]
                try:
                    priority = Priority(bracket.lower())
                except ValueError:
                    pass
                clean = clean.replace(f"[{bracket}]", "").strip()
            follow_ups.append(FollowUp(description=clean, owner=owner, priority=priority))

    return follow_ups


def _parse_automation(text: str) -> list[AutomationCandidate]:
    """Parse automation/delegation candidates."""
    section_text = _extract_section(text, "DELEGATION") or _extract_section(text, "AUTOMATION")
    if not section_text:
        return []

    candidates = []
    for line in section_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") or (stripped[0].isdigit() and "." in stripped[:3]):
            clean = stripped.lstrip("-0123456789.) ").strip()
            candidates.append(AutomationCandidate(
                description=clean,
                rationale="",
            ))

    return candidates


def _parse_key_themes(text: str) -> list[str]:
    """Parse key themes from the KEY THEMES section."""
    section_text = _extract_section(text, "KEY THEMES")
    if not section_text:
        return []

    themes = []
    for line in section_text.split("\n"):
        stripped = line.strip()
        if stripped and (stripped.startswith("-") or stripped[0].isdigit()):
            themes.append(stripped.lstrip("-0123456789.) ").strip())

    return themes
