"""
Self-learning loop.

Brain produces outputs (briefings, call analyses, lens results). Hermes
delivers them to Jim. Jim reacts — a thumbs up/down, a correction, a note.
Hermes posts those reactions back. This module turns that stream of
reactions into something Brain actually *learns* from:

    output ──▶ Jim reacts ──▶ feedback stored
        ──▶ reflection distills lessons
        ──▶ lessons injected into the next prompt
        ──▶ better output ──▶ ...

Two layers:

  • Feedback  — raw, append-only record of every reaction (data/feedback/).
  • Lessons   — a distilled, evolving set of preferences Brain has learned
                (data/learning/lessons.json). Reflection rewrites these from
                accumulated feedback using Claude.

The generation modules call `lessons_block(category)` (no model call, just
a file read) and append it to their system prompt. Reflection — the part
that actually updates what Brain believes — runs on a schedule or when
enough new feedback accumulates.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


TargetKind = Literal["briefing", "analysis", "lens"]
Rating = Literal["up", "down", "neutral"]

# Which lesson categories apply when generating each kind of output.
_CATEGORY_MAP = {
    "briefing": ("briefing", "global"),
    "analysis": ("analysis", "global"),
    "lens": ("lens", "global"),
}


class FeedbackRecord(BaseModel):
    """One reaction from Jim about one Brain output."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_kind: TargetKind
    target_ref: str = ""            # outgoing id / filename the feedback is about
    rating: Rating = "neutral"
    note: str = ""                  # free-text from Jim ("too long", "wrong owner")
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed: bool = False         # folded into lessons yet?


class Lesson(BaseModel):
    """A durable preference Brain has learned about how to serve Jim."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    category: str = "global"        # briefing | analysis | lens | global
    text: str
    evidence_count: int = 1
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningStore:
    """Persists feedback + lessons and runs the reflection step."""

    def __init__(
        self,
        feedback_dir: str | None = None,
        learning_dir: str | None = None,
    ):
        self.feedback_dir = Path(
            feedback_dir or os.environ.get("BRAIN_FEEDBACK_DIR", "./data/feedback")
        )
        self.learning_dir = Path(
            learning_dir or os.environ.get("BRAIN_LEARNING_DIR", "./data/learning")
        )
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_path = self.learning_dir / "lessons.json"

    # ── Feedback ─────────────────────────────────────────────────────────────

    def record_feedback(self, fb: FeedbackRecord) -> FeedbackRecord:
        path = self.feedback_dir / f"fb_{fb.id}.json"
        path.write_text(json.dumps(fb.model_dump(mode="json"), indent=2),
                        encoding="utf-8")
        return fb

    def _load_feedback(self, path: Path) -> Optional[FeedbackRecord]:
        try:
            return FeedbackRecord(**json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            return None

    def list_feedback(self, unprocessed_only: bool = False) -> list[FeedbackRecord]:
        out = []
        for p in self.feedback_dir.glob("fb_*.json"):
            fb = self._load_feedback(p)
            if fb and (not unprocessed_only or not fb.processed):
                out.append(fb)
        out.sort(key=lambda f: f.created_at)
        return out

    def _mark_processed(self, ids: list[str]) -> None:
        idset = set(ids)
        for p in self.feedback_dir.glob("fb_*.json"):
            fb = self._load_feedback(p)
            if fb and fb.id in idset and not fb.processed:
                fb.processed = True
                p.write_text(json.dumps(fb.model_dump(mode="json"), indent=2),
                             encoding="utf-8")

    # ── Lessons ──────────────────────────────────────────────────────────────

    def get_lessons(self) -> list[Lesson]:
        if not self.lessons_path.exists():
            return []
        try:
            data = json.loads(self.lessons_path.read_text(encoding="utf-8"))
            return [Lesson(**l) for l in data.get("lessons", [])]
        except Exception:
            return []

    def _save_lessons(self, lessons: list[Lesson]) -> None:
        payload = {
            "lessons": [l.model_dump(mode="json") for l in lessons],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.lessons_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def lessons_block(self, category: str) -> str:
        """Render lessons relevant to `category` as a system-prompt block.

        Pure file read — safe to call on every generation. Returns "" when
        Brain hasn't learned anything yet, so prompts are unchanged at first.
        """
        wanted = set(_CATEGORY_MAP.get(category, (category, "global")))
        relevant = [l for l in self.get_lessons() if l.category in wanted]
        if not relevant:
            return ""
        lines = [
            "",
            "What you've learned about Jim's preferences (apply these — they",
            "come from his direct feedback on your past work):",
        ]
        for l in relevant:
            lines.append(f"- {l.text}")
        return "\n".join(lines)

    # ── Reflection (the learning step) ───────────────────────────────────────

    def reflect(self, max_feedback: int = 50) -> dict:
        """Fold unprocessed feedback into the lesson set using Claude.

        This is where Brain actually updates what it believes. Returns a
        summary dict. No-op (and no model call) when there's no new feedback.
        """
        new = self.list_feedback(unprocessed_only=True)[:max_feedback]
        if not new:
            return {"updated": False, "reason": "no new feedback",
                    "lesson_count": len(self.get_lessons())}

        current = self.get_lessons()

        from brain.client import get_client, get_model
        client = get_client()
        model = get_model()

        current_block = "\n".join(
            f"[{l.id}] ({l.category}) {l.text}  (evidence: {l.evidence_count})"
            for l in current
        ) or "(none yet)"

        feedback_block = "\n".join(
            f"- on {f.target_kind} [{f.rating}] "
            f"{('tags=' + ','.join(f.tags) + ' ') if f.tags else ''}"
            f"{f.note or '(no note)'}"
            for f in new
        )

        prompt = (
            "You maintain a set of LESSONS describing how the Operations "
            "Co-Founder should tailor its work to Jim Harshaw Jr.'s "
            "preferences. Update the lessons using new feedback.\n\n"
            "Rules:\n"
            "- Merge feedback that confirms an existing lesson (bump it, don't "
            "duplicate). Refine wording when feedback sharpens it.\n"
            "- Add a new lesson only for a clear, repeatable preference.\n"
            "- Drop lessons that new feedback contradicts.\n"
            "- Keep lessons concrete and actionable. Max 15 lessons total.\n"
            "- category must be one of: briefing, analysis, lens, global.\n\n"
            f"CURRENT LESSONS:\n{current_block}\n\n"
            f"NEW FEEDBACK:\n{feedback_block}\n\n"
            "Return ONLY a JSON object: "
            '{\"lessons\":[{\"category\":\"...\",\"text\":\"...\",'
            '\"evidence_count\":N}, ...]}. No prose.'
        )

        resp = client.messages.create(
            model=model,
            max_tokens=1500,
            temperature=0.3,
            system=("You distill durable preferences from feedback. You are "
                    "conservative: you only encode patterns, never one-offs."),
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text

        lessons = self._parse_lessons(raw)
        if lessons is None:
            return {"updated": False, "reason": "could not parse reflection",
                    "lesson_count": len(current)}

        self._save_lessons(lessons)
        self._mark_processed([f.id for f in new])
        return {
            "updated": True,
            "processed_feedback": len(new),
            "lesson_count": len(lessons),
            "lessons": [l.text for l in lessons],
        }

    @staticmethod
    def _parse_lessons(raw: str) -> Optional[list[Lesson]]:
        """Pull the JSON lessons array out of a model response, robustly."""
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            data = json.loads(raw[start : end + 1])
        except Exception:
            return None
        items = data.get("lessons")
        if not isinstance(items, list):
            return None
        lessons: list[Lesson] = []
        for it in items:
            text = (it.get("text") or "").strip()
            if not text:
                continue
            cat = it.get("category", "global")
            if cat not in ("briefing", "analysis", "lens", "global"):
                cat = "global"
            lessons.append(Lesson(
                category=cat,
                text=text,
                evidence_count=int(it.get("evidence_count", 1) or 1),
            ))
        return lessons


# Module-level singleton + convenience for generators.
_store: Optional[LearningStore] = None


def get_store() -> LearningStore:
    global _store
    if _store is None:
        _store = LearningStore()
    return _store


def lessons_block(category: str) -> str:
    """Convenience: learned-preferences block for a given output category."""
    try:
        return get_store().lessons_block(category)
    except Exception:
        return ""  # learning must never break generation
