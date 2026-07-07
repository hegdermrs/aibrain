"""
Core data models for the Operations Co-Founder Brain.
All data structures use Pydantic for validation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────


class BriefingType(str, Enum):
    MORNING = "morning"
    EVENING = "evening"


class SignalSource(str, Enum):
    EMAIL = "email"
    SKOOL = "skool"
    TELEGRAM = "telegram"
    TRANSCRIPT = "transcript"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    DECIDED = "decided"
    DEFERRED = "deferred"


# ── Hermes Signals ───────────────────────────────────────────────────────────


class HermesSignal(BaseModel):
    """A single surfaced item from Hermes (email, Skool post, etc.)."""
    id: str
    source: SignalSource
    title: str
    summary: str
    priority: Priority = Priority.MEDIUM
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_text: str = Field(default="", description="Full original text")
    sender: Optional[str] = None
    thread_id: Optional[str] = None
    requires_response: bool = False


class HermesDigest(BaseModel):
    """Batch of signals Hermes surfaces for the brain to process."""
    signals: list[HermesSignal]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_window_start: datetime
    time_window_end: datetime


# ── Metrics ──────────────────────────────────────────────────────────────────


class BusinessMetric(BaseModel):
    """A single business metric surfaced by Hermes."""
    name: str
    value: float
    previous_value: Optional[float] = None
    unit: str = ""
    trend: Optional[str] = None  # "up", "down", "flat"
    note: Optional[str] = None


class MetricsSnapshot(BaseModel):
    """Collection of business metrics for a time window."""
    metrics: list[BusinessMetric]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Call Transcript ──────────────────────────────────────────────────────────


class TranscriptSegment(BaseModel):
    """A meaningful chunk of a call transcript with speaker attribution."""
    speaker: str
    text: str
    start_time: float  # seconds from start
    end_time: float


class CallTranscript(BaseModel):
    """Full transcript of a call (Fathom/Zoom/Meet)."""
    id: str
    title: str
    date: datetime
    participants: list[str]
    segments: list[TranscriptSegment]
    full_text: str  # raw transcript text
    source: str = ""  # "fathom", "zoom", "meet"
    duration_minutes: float = 0.0


# ── Call Analysis ────────────────────────────────────────────────────────────


class Decision(BaseModel):
    """A decision surfaced from a call transcript."""
    description: str
    made_by: str
    context: str = ""
    status: DecisionStatus = DecisionStatus.DECIDED


class FollowUp(BaseModel):
    """A follow-up item surfaced from a call."""
    description: str
    owner: str
    deadline: Optional[str] = None
    priority: Priority = Priority.MEDIUM


class AutomationCandidate(BaseModel):
    """Something identified as ready to delegate or automate."""
    description: str
    rationale: str
    type: str = ""  # "delegate" or "automate"
    estimated_effort: str = ""  # "low", "medium", "high"


class CallAnalysis(BaseModel):
    """Complete analysis output for a single call transcript."""
    call_id: str
    call_title: str
    summary: str
    decisions: list[Decision] = Field(default_factory=list)
    follow_ups: list[FollowUp] = Field(default_factory=list)
    automation_candidates: list[AutomationCandidate] = Field(default_factory=list)
    key_themes: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Daily Briefing ───────────────────────────────────────────────────────────


class BriefingSection(BaseModel):
    """A single section within a daily briefing."""
    heading: str
    content: str
    priority: Priority = Priority.MEDIUM


class DailyBriefing(BaseModel):
    """Complete daily briefing (morning or evening)."""
    briefing_type: BriefingType
    date: datetime = Field(default_factory=datetime.utcnow)
    headline: str  # one-line executive summary
    sections: list[BriefingSection]
    key_metrics: list[BusinessMetric] = Field(default_factory=list)
    requires_jim_attention: list[str] = Field(
        default_factory=list,
        description="Items that specifically need Jim's decision or input"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Strategic Lens ───────────────────────────────────────────────────────────


class PersonaConfig(BaseModel):
    """Configuration for a strategic persona."""
    name: str
    tagline: str = ""
    description: str
    thinking_style: str
    key_questions: list[str] = Field(default_factory=list)
    biases: list[str] = Field(default_factory=list)


class LensQuery(BaseModel):
    """A question or decision to pressure-test through the lens."""
    question: str
    context: str = ""
    personas: list[str] = Field(default_factory=list)  # persona names to use
    constraints: list[str] = Field(default_factory=list)


class PersonaResponse(BaseModel):
    """A single persona's analysis of a question."""
    persona_name: str
    analysis: str
    key_insight: str = ""
    recommended_action: str = ""


class LensResult(BaseModel):
    """Complete strategic lens output."""
    query: LensQuery
    persona_responses: list[PersonaResponse]
    synthesis: str  # cross-persona synthesis
    generated_at: datetime = Field(default_factory=datetime.utcnow)
