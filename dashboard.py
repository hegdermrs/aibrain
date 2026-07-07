"""
Operations Co-Founder — Dashboard
Modern Streamlit web UI for Jim's coaching business.

Run: streamlit run dashboard.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="Operations Co-Founder",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Status badge styling */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .status-good {
        background-color: #d1f7d6;
        color: #0d6b3c;
    }

    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }

    .status-error {
        background-color: #fee2e2;
        color: #7f1d1d;
    }

    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1f2937;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.25rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
    }

    /* Better spacing */
    .spacer {
        margin: 1rem 0;
    }

    /* Button styling */
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }

    /* Container borders */
    div[data-testid="stContainer"] {
        border-radius: 0.75rem;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# Local imports
from brain.models import (
    BriefingType,
    CallTranscript,
    LensQuery,
    Priority,
)
from brain.briefing import generate_briefing
from brain.analyst import analyze_transcript
from brain.lens import run_lens_parallel
from brain.hermes_interface import HermesInterface
from brain.personas import get_registry


# ── Helpers ─────────────────────────────────────────────────────────────────

def _has_api_key() -> bool:
    import os
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _get_status_color(minutes_ago: float | None) -> tuple[str, str, str]:
    """Return (color_class, emoji, status_text) based on age."""
    if minutes_ago is None:
        return "status-error", "⚠️", "No data"
    elif minutes_ago < 60:
        return "status-good", "✅", "Live"
    elif minutes_ago < 180:
        return "status-warning", "⏱️", "Stale"
    else:
        return "status-error", "❌", "Offline"


def _format_timestamp(ts) -> str:
    """Format datetime for display."""
    if isinstance(ts, str):
        return ts[:19].replace("T", " ")
    return ts.strftime("%b %d, %Y at %I:%M %p")


def _priority_badge(priority) -> str:
    """Return emoji for priority level."""
    if isinstance(priority, Priority):
        priority = priority.value
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "")


def _list_saved(dir_path: Path, suffix: str) -> list[Path]:
    """List saved output files, newest first."""
    if not dir_path.exists():
        return []
    return sorted(dir_path.glob(f"*{suffix}"), reverse=True)


def _load_json(path: Path) -> dict:
    """Load a JSON file safely."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("# 🧠 Operations Co-Founder")
    st.caption("AI brain for Jim Harshaw Jr.'s coaching business")

    # Status section
    st.markdown("---")
    st.markdown("### 📊 System Status")

    hermes = HermesInterface()
    digest_age = hermes.hermes_digest_age_minutes()
    status_class, status_emoji, status_text = _get_status_color(digest_age)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hermes Connection", status_text, f"{digest_age:.0f}min ago" if digest_age else "No data")
    with col2:
        api_ok = _has_api_key()
        st.metric("Claude API", "✅ Ready" if api_ok else "❌ Error", "Connected" if api_ok else "No key")

    # Navigation
    st.markdown("---")
    st.markdown("### 🗂️ Navigation")

    page = st.radio(
        "Select a page:",
        ["📋 Briefing", "📞 Analyze Call", "🔍 Strategic Lens", "📚 History"],
        label_visibility="collapsed",
    )

    # Help section
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    with st.expander("How to use"):
        st.markdown("""
        **📋 Briefing** — Generate morning/evening updates from Hermes signals

        **📞 Analyze Call** — Upload transcripts to surface decisions & follow-ups

        **🔍 Lens** — Pressure-test decisions through strategic personas

        **📚 History** — Browse past analyses and briefings

        **Pro tip:** Hermes surfaces signals via JSON files. Make sure Hermes is running!
        """)

    st.markdown("---")
    st.markdown("<sub>Brain thinks. Hermes acts.</sub>", unsafe_allow_html=True)
    st.markdown(f"<sub>v0.1.0 | {datetime.now().strftime('%b %d, %Y')}</sub>", unsafe_allow_html=True)


# ── Constants ───────────────────────────────────────────────────────────────

BRIEFINGS_DIR = Path("data/briefings")
ANALYSIS_DIR = Path("data/analysis")
HERMES = HermesInterface()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Generate Briefing
# ═════════════════════════════════════════════════════════════════════════════

if page == "📋 Briefing":
    st.markdown("<h1 class='main-header'>📋 Daily Briefing</h1>", unsafe_allow_html=True)
    st.markdown("Synthesize signals from Hermes into a morning or evening update for Jim.", unsafe_allow_html=True)
    st.markdown("---")

    # Control panel
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        briefing_type = st.radio(
            "Briefing Type",
            ["Morning ☀️", "Evening 🌙"],
            label_visibility="collapsed",
        )
        bt_clean = briefing_type.split()[0]

    with col2:
        digest_age = HERMES.hermes_digest_age_minutes()
        if digest_age is not None:
            age_text = f"{digest_age:.0f}m" if digest_age < 120 else f"{digest_age/60:.1f}h"
            status_class, emoji, _ = _get_status_color(digest_age)
            st.metric("Hermes Data", age_text, f"{emoji} Fresh")
        else:
            st.metric("Hermes Data", "None", "⚠️ Waiting")

    with col3:
        st.empty()  # Spacing

    # Data preview section
    digest = HERMES.read_latest_digest()
    if digest:
        with st.expander("📡 Incoming Signals", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Signals", len(digest.signals))
            with col2:
                high_priority = sum(1 for s in digest.signals if s.priority.value == "high")
                st.metric("🔴 High Priority", high_priority)
            with col3:
                requires_response = sum(1 for s in digest.signals if s.requires_response)
                st.metric("💬 Need Response", requires_response)

            st.markdown("**Recent signals:**")
            for s in digest.signals[:8]:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(s.priority.value, "")
                response_flag = "💬" if s.requires_response else ""
                st.markdown(f"{priority_emoji} **{s.source.value.upper()}**: {s.title} {response_flag}")

    # Generate button
    if digest:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Generate Briefing", type="primary", use_container_width=True, disabled=not _has_api_key()):
                with st.spinner(f"Generating {bt_clean} briefing... ~15-30 seconds"):
                    try:
                        metrics = HERMES.read_metrics()
                        bt = BriefingType.MORNING if bt_clean == "Morning" else BriefingType.EVENING
                        result = generate_briefing(digest=digest, metrics=metrics, briefing_type=bt)

                        # Save
                        ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
                        out_path = BRIEFINGS_DIR / f"{bt_clean.lower()}_{ts}.json"
                        BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
                        out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2, default=str))

                        st.success(f"✅ {bt_clean.title()} briefing generated and saved!")
                        st.balloons()

                        # Display in tabs
                        tab1, tab2, tab3 = st.tabs(["📄 Content", "📊 Metrics", "⚠️ Action Items"])

                        with tab1:
                            emoji = "☀️" if bt_clean == "Morning" else "🌙"
                            st.markdown(f"## {emoji} {result.headline}")
                            for section in result.sections:
                                with st.container(border=True):
                                    st.markdown(f"### {section.heading}")
                                    st.markdown(section.content)

                        with tab2:
                            if result.key_metrics:
                                cols = st.columns(min(3, len(result.key_metrics)))
                                for i, m in enumerate(result.key_metrics):
                                    with cols[i % 3]:
                                        delta = None
                                        if m.previous_value is not None:
                                            delta = f"{m.value - m.previous_value:.1f}{m.unit}"
                                        st.metric(m.name, f"{m.value}{m.unit}", delta=delta)
                            else:
                                st.info("No metrics available")

                        with tab3:
                            if result.requires_jim_attention:
                                st.markdown("### Items Requiring Jim's Attention")
                                for i, item in enumerate(result.requires_jim_attention, 1):
                                    st.markdown(f"**{i}.** {item}")
                            else:
                                st.success("No blocker items!")

                    except Exception as e:
                        st.error(f"Failed to generate briefing: {str(e)}")
    else:
        st.info("⏳ Waiting for data from Hermes...")

    # Recent briefings
    st.markdown("---")
    st.markdown("### 📚 Recent Briefings")
    recent = _list_saved(BRIEFINGS_DIR, ".json")[:5]
    if recent:
        for path in recent:
            data = _load_json(path)
            if data:
                bt = data.get("briefing_type", "?").title()
                headline = data.get("headline", "No headline")[:100]
                st.markdown(f"**{bt}** ({path.stem})")
                st.caption(headline)
    else:
        st.caption("No briefings generated yet.")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Analyze Call
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📞 Analyze Call":
    st.markdown("<h1 class='main-header'>📞 Call Analysis</h1>", unsafe_allow_html=True)
    st.markdown("Extract decisions, follow-ups, and delegation targets from transcripts.", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["📎 Upload & Analyze", "📂 Recent Transcripts"])

    with tab1:
        st.markdown("#### Upload a transcript JSON file")
        st.caption("Files from Fathom, Zoom, or Meet (via Hermes) work here.")

        uploaded_file = st.file_uploader(
            "Choose a transcript JSON",
            type=["json"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            try:
                data = json.loads(uploaded_file.read())
                transcript = CallTranscript(**data)

                # Show transcript info in card format
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Title", transcript.title[:30])
                    with col2:
                        st.metric("Duration", f"{transcript.duration_minutes:.0f} min")
                    with col3:
                        st.metric("Participants", len(transcript.participants))

                    st.markdown(f"**Date:** {_format_timestamp(transcript.date)}")
                    st.markdown(f"**Participants:** {', '.join(transcript.participants)}")

                with st.expander("📄 Preview transcript (first 2000 chars)", expanded=False):
                    st.text_area("Transcript preview", transcript.full_text[:2000], height=150, disabled=True)

                if st.button("🚀 Analyze This Call", type="primary", use_container_width=True, disabled=not _has_api_key()):
                    with st.spinner("Analyzing... ~20-40 seconds"):
                        try:
                            result = analyze_transcript(transcript)

                            # Save
                            ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
                            out_path = ANALYSIS_DIR / f"call_{ts}.json"
                            ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
                            out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2, default=str))

                            st.success("✅ Analysis complete!")
                            st.balloons()

                            # Tabbed results
                            tab_summary, tab_decisions, tab_followups, tab_automation, tab_themes = st.tabs(
                                ["📝 Summary", "✅ Decisions", "📌 Follow-ups", "🤖 Automate", "🔑 Themes"]
                            )

                            with tab_summary:
                                st.markdown(result.summary)

                            with tab_decisions:
                                if result.decisions:
                                    for i, d in enumerate(result.decisions, 1):
                                        with st.container(border=True):
                                            st.markdown(f"**Decision {i}:** {d.description}")
                                            st.caption(f"Made by: {d.made_by}")
                                else:
                                    st.info("No decisions recorded")

                            with tab_followups:
                                if result.follow_ups:
                                    for f in result.follow_ups:
                                        badge = _priority_badge(f.priority)
                                        with st.container(border=True):
                                            st.markdown(f"{badge} **{f.description}**")
                                            st.caption(f"Owner: {f.owner}" + (f" | Due: {f.deadline}" if f.deadline else ""))
                                else:
                                    st.info("No follow-ups")

                            with tab_automation:
                                if result.automation_candidates:
                                    for a in result.automation_candidates:
                                        with st.container(border=True):
                                            st.markdown(f"**{a.description}**")
                                            if a.rationale:
                                                st.markdown(f"_{a.rationale}_")
                                else:
                                    st.info("No automation candidates")

                            with tab_themes:
                                if result.key_themes:
                                    for t in result.key_themes:
                                        st.markdown(f"• {t}")
                                else:
                                    st.info("No themes identified")

                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")

            except Exception as e:
                st.error(f"Could not parse transcript: {str(e)}")

    with tab2:
        st.markdown("#### Transcripts saved by Hermes (last 30 days)")

        transcripts = HERMES.read_transcripts_since(
            datetime.utcnow() - timedelta(days=30)
        )

        if transcripts:
            for t in transcripts:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    with st.expander(f"**{t.title}** — {_format_timestamp(t.date)}"):
                        st.markdown(f"**Duration:** {t.duration_minutes:.0f} min")
                        st.markdown(f"**Participants:** {', '.join(t.participants)}")

                with col2:
                    if st.button("📊 Analyze", key=f"analyze_{t.id}", use_container_width=True):
                        with st.spinner("Analyzing..."):
                            try:
                                result = analyze_transcript(t)
                                ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
                                out_path = ANALYSIS_DIR / f"call_{ts}.json"
                                ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
                                out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2, default=str))
                                st.success("✅ Analysis saved! Check History.")
                            except Exception as e:
                                st.error(f"Failed: {e}")

                with col3:
                    st.markdown("")  # Spacing

        else:
            st.info("📭 No transcripts found in the last 30 days")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Strategic Lens
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🔍 Strategic Lens":
    st.markdown("<h1 class='main-header'>🔍 Strategic Lens</h1>", unsafe_allow_html=True)
    st.markdown("Pressure-test decisions through multiple strategic lenses.", unsafe_allow_html=True)
    st.markdown("---")

    registry = get_registry()
    available = registry.get_all()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 🎯 Your Question or Decision")
        question = st.text_area(
            "What do you want to explore?",
            placeholder="e.g. 'Should we raise prices from $500 to $750/mo?'",
            height=100,
            label_visibility="collapsed",
        )

        st.markdown("#### 📋 Context")
        context = st.text_area(
            "Background info",
            placeholder="e.g. '40 clients at $500/mo. Waitlist of 15. Competitors charge $800-1200.'",
            height=80,
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("#### 👥 Choose Personas")
        selected = []
        for p in available:
            if st.checkbox(f"{p.name}", value=True, key=f"persona_{p.name}"):
                selected.append(p.name)

        st.markdown("#### 🔗 Constraints")
        constraints = st.text_area(
            "Limits to consider",
            placeholder="e.g. Must keep retention > 90%",
            height=80,
            label_visibility="collapsed",
        )

        st.metric("Personas Selected", len(selected))

    # Info about personas
    if st.button("ℹ️ Learn about personas", use_container_width=True):
        st.markdown("---")
        st.markdown("### About Each Persona")
        for p in available:
            with st.container(border=True):
                st.markdown(f"#### {p.name}")
                st.markdown(f"_{p.tagline}_")
                st.markdown(f"**Thinking style:** {p.thinking_style[:200]}...")

    # Main analysis button
    st.markdown("---")
    if st.button("🚀 Run Lens Analysis", type="primary", use_container_width=True, disabled=not (_has_api_key() and question.strip() and selected)):
        if not question.strip():
            st.warning("Please enter a question.")
        elif not selected:
            st.warning("Select at least one persona.")
        else:
            constraints_list = [c.strip() for c in constraints.split("\n") if c.strip()]
            query = LensQuery(
                question=question.strip(),
                context=context.strip(),
                personas=selected,
                constraints=constraints_list,
            )

            with st.spinner(f"Analyzing with {len(selected)} persona(s)... ~20-60 seconds"):
                try:
                    result = run_lens_parallel(query)

                    # Save
                    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
                    out_path = ANALYSIS_DIR / f"lens_{ts}.json"
                    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2, default=str))

                    st.success("✅ Analysis complete!")
                    st.balloons()

                    # Results tabs
                    tab_personas = st.tabs([f"{r.persona_name}" for r in result.persona_responses] + ["🧠 Synthesis"])

                    for i, r in enumerate(result.persona_responses):
                        with tab_personas[i]:
                            st.markdown(f"### {r.persona_name}")
                            st.markdown(r.analysis)

                    with tab_personas[-1]:
                        st.markdown("## 🧠 Cross-Persona Synthesis")
                        st.markdown(result.synthesis)

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: History
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📚 History":
    st.markdown("<h1 class='main-header'>📚 History</h1>", unsafe_allow_html=True)
    st.markdown("Browse all past analyses, briefings, and strategic explorations.", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["☀️ Briefings", "📞 Call Analyses", "🔍 Lens Results"])

    with tab1:
        st.markdown("### Daily Briefings")
        briefings = _list_saved(BRIEFINGS_DIR, ".json")[:50]
        if not briefings:
            st.info("No briefings yet. Generate one!")
        else:
            cols = st.columns(1)
            for path in briefings:
                data = _load_json(path)
                if not data:
                    continue
                bt = data.get("briefing_type", "?").title()
                emoji = "☀️" if bt == "Morning" else "🌙"
                headline = data.get("headline", "")[:120]
                generated = data.get("generated_at", "?")

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{emoji} {bt}** — {headline}")
                        st.caption(f"Generated: {generated}")
                    with col2:
                        if st.button("👁️ View", key=f"view_brief_{path.stem}", use_container_width=True):
                            with st.expander("Full Briefing", expanded=True):
                                for section in data.get("sections", []):
                                    st.markdown(f"**{section.get('heading', '')}**")
                                    st.markdown(section.get("content", ""))
                                if data.get("requires_jim_attention"):
                                    st.warning("⚠️ Required Jim: " + ", ".join(data["requires_jim_attention"]))

    with tab2:
        st.markdown("### Call Analyses")
        all_files = _list_saved(ANALYSIS_DIR, ".json")
        analyses = [f for f in all_files if "lens_" not in f.name][:50]
        if not analyses:
            st.info("No call analyses yet.")
        else:
            for path in analyses:
                data = _load_json(path)
                if not data:
                    continue
                call_title = data.get("call_title", "?")
                summary = data.get("summary", "")[:150]
                generated = data.get("generated_at", "?")

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📞 {call_title}**")
                        st.markdown(f"_{summary}_")
                        st.caption(f"Generated: {generated}")
                    with col2:
                        if st.button("📊 View", key=f"view_call_{path.stem}", use_container_width=True):
                            with st.expander("Full Analysis", expanded=True):
                                decisions = data.get("decisions", [])
                                follow_ups = data.get("follow_ups", [])
                                automation = data.get("automation_candidates", [])

                                if decisions:
                                    st.markdown("**✅ Decisions:**")
                                    for d in decisions:
                                        st.markdown(f"- {d.get('description', '')}")

                                if follow_ups:
                                    st.markdown("**📌 Follow-ups:**")
                                    for f in follow_ups:
                                        priority_badge = _priority_badge(f.get("priority", "medium"))
                                        st.markdown(f"{priority_badge} {f.get('description', '')} → {f.get('owner', '?')}")

                                if automation:
                                    st.markdown("**🤖 Automate/Delegate:**")
                                    for a in automation:
                                        st.markdown(f"- {a.get('description', '')}")

    with tab3:
        st.markdown("### Strategic Lens Results")
        lens_results = _list_saved(ANALYSIS_DIR, "lens_*.json")[:50]
        if not lens_results:
            st.info("No lens results yet.")
        else:
            for path in lens_results:
                data = _load_json(path)
                if not data:
                    continue
                query_data = data.get("query", {})
                question = query_data.get("question", "?")[:100]
                generated = data.get("generated_at", "?")
                personas = [r.get("persona_name", "?") for r in data.get("persona_responses", [])]

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**🔍 {question}**")
                        st.caption(f"Personas: {', '.join(personas)} | Generated: {generated}")
                    with col2:
                        if st.button("📋 View", key=f"view_lens_{path.stem}", use_container_width=True):
                            with st.expander("Full Analysis", expanded=True):
                                for r in data.get("persona_responses", []):
                                    st.markdown(f"**{r.get('persona_name', '?')}**")
                                    st.markdown(r.get("key_insight", r.get("analysis", ""))[:300])
                                    st.divider()
                                synthesis = data.get("synthesis", "")
                                if synthesis:
                                    st.markdown("**🧠 Synthesis**")
                                    st.markdown(synthesis[:800])
