"""
Telegram formatting — turn Brain's structured output into clean,
delivery-ready text for Hermes to send to Jim.

Kept separate from the analysis logic so the wire format can change
without touching how Brain thinks. Uses Telegram-flavoured Markdown
(*bold*, simple bullets) which renders well and degrades gracefully
to plain text if Hermes sends it raw.
"""

from __future__ import annotations

from brain.models import CallAnalysis, DailyBriefing, BriefingType


_PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def format_briefing(briefing: DailyBriefing) -> str:
    """Render a DailyBriefing as Telegram text."""
    emoji = "☀️" if briefing.briefing_type == BriefingType.MORNING else "🌙"
    label = "Morning" if briefing.briefing_type == BriefingType.MORNING else "Evening"
    lines: list[str] = [f"{emoji} *{label} Briefing*", ""]

    if briefing.headline:
        lines.append(briefing.headline)
        lines.append("")

    for section in briefing.sections:
        lines.append(f"*{section.heading}*")
        lines.append(section.content)
        lines.append("")

    if briefing.requires_jim_attention:
        lines.append("⚠️ *Needs Jim*")
        for item in briefing.requires_jim_attention:
            lines.append(f"• {item}")
        lines.append("")

    if briefing.key_metrics:
        lines.append("📊 *Metrics*")
        for m in briefing.key_metrics:
            delta = ""
            if m.previous_value is not None:
                diff = m.value - m.previous_value
                arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "—")
                delta = f" {arrow}{abs(diff):g}{m.unit}"
            lines.append(f"• {m.name}: {m.value:g}{m.unit}{delta}")

    return "\n".join(lines).strip()


def format_analysis(analysis: CallAnalysis) -> str:
    """Render a CallAnalysis as Telegram text."""
    lines: list[str] = [f"📞 *Call Analysis — {analysis.call_title}*", ""]

    if analysis.summary:
        lines.append(analysis.summary)
        lines.append("")

    if analysis.decisions:
        lines.append("*✅ Decisions*")
        for d in analysis.decisions:
            who = f" — {d.made_by}" if d.made_by else ""
            lines.append(f"• {d.description}{who}")
        lines.append("")

    if analysis.follow_ups:
        lines.append("*📌 Follow-ups*")
        for f in analysis.follow_ups:
            badge = _PRIORITY_EMOJI.get(
                f.priority.value if hasattr(f.priority, "value") else str(f.priority),
                "",
            )
            due = f" (due {f.deadline})" if f.deadline else ""
            lines.append(f"{badge} {f.description} → *{f.owner}*{due}")
        lines.append("")

    if analysis.automation_candidates:
        lines.append("*🤖 Delegate / Automate*")
        for a in analysis.automation_candidates:
            lines.append(f"• {a.description}")
        lines.append("")

    if analysis.key_themes:
        lines.append("*🔑 Themes*")
        for t in analysis.key_themes:
            lines.append(f"• {t}")

    return "\n".join(lines).strip()
