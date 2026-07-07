"""
Hermes Interface — Pure data consumption layer.

The brain reads what Hermes surfaces. No outbound connections.
Hermes owns Skool browser, Gmail, Telegram. The brain only
consumes the structured data Hermes drops into the filesystem.

Design: file-based integration. Hermes writes JSON/YAML digests
into designated directories. The brain reads and processes them.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from brain.models import (
    BusinessMetric,
    CallTranscript,
    HermesDigest,
    HermesSignal,
    MetricsSnapshot,
    SignalSource,
)


class HermesInterface:
    """
    Reads structured data surfaced by Hermes from the filesystem.
    Hermes is responsible for writing digests. The brain reads them.
    """

    def __init__(
        self,
        digest_dir: str | None = None,
        transcript_dir: str | None = None,
    ):
        self.digest_dir = Path(
            digest_dir
            or os.environ.get("HERMES_DIGEST_DIR", "./data/incoming")
        )
        self.transcript_dir = Path(
            transcript_dir
            or os.environ.get("HERMES_TRANSCRIPT_DIR", "./data/transcripts")
        )

    # ── Digest (signals + metrics) ──────────────────────────────────────────

    def read_latest_digest(self) -> Optional[HermesDigest]:
        """Read the most recent digest Hermes dropped."""
        files = sorted(self.digest_dir.glob("digest_*.json"), reverse=True)
        if not files:
            return None
        return self._parse_digest_file(files[0])

    def read_digest_for_window(
        self, start: datetime, end: datetime
    ) -> Optional[HermesDigest]:
        """Read a digest covering a specific time window."""
        for f in sorted(self.digest_dir.glob("digest_*.json"), reverse=True):
            digest = self._parse_digest_file(f)
            if digest and digest.time_window_start <= start and digest.time_window_end >= end:
                return digest
        return None

    def read_digests_since(self, since: datetime) -> list[HermesDigest]:
        """Read all digests after a given timestamp."""
        digests = []
        for f in sorted(self.digest_dir.glob("digest_*.json"), reverse=True):
            digest = self._parse_digest_file(f)
            if digest and digest.generated_at >= since:
                digests.append(digest)
        return digests

    def read_metrics(self) -> MetricsSnapshot:
        """Read the latest metrics snapshot from Hermes."""
        files = sorted(self.digest_dir.glob("metrics_*.json"), reverse=True)
        if files:
            data = json.loads(files[0].read_text(encoding="utf-8"))
            return MetricsSnapshot(**data)
        return MetricsSnapshot(metrics=[])

    # ── Transcripts ─────────────────────────────────────────────────────────

    def read_latest_transcript(self) -> Optional[CallTranscript]:
        """Read the most recent call transcript."""
        files = sorted(self.transcript_dir.glob("transcript_*.json"), reverse=True)
        if not files:
            return None
        data = json.loads(files[0].read_text(encoding="utf-8"))
        return CallTranscript(**data)

    def read_transcripts_since(self, since: datetime) -> list[CallTranscript]:
        """Read all transcripts after a given date."""
        transcripts = []
        for f in sorted(self.transcript_dir.glob("transcript_*.json"), reverse=True):
            data = json.loads(f.read_text(encoding="utf-8"))
            t = CallTranscript(**data)
            if t.date >= since:
                transcripts.append(t)
        return transcripts

    def read_transcript(self, transcript_id: str) -> Optional[CallTranscript]:
        """Read a specific transcript by ID."""
        path = self.transcript_dir / f"transcript_{transcript_id}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return CallTranscript(**data)
        return None

    # ── Status ──────────────────────────────────────────────────────────────

    def hermse_digest_age_minutes(self) -> Optional[float]:
        """How stale is the latest digest? None if no digest exists."""
        digest = self.read_latest_digest()
        if digest is None:
            return None
        # Use timezone-aware UTC now to compare with digest.generated_at
        now = datetime.now(timezone.utc)
        # If digest timestamp is naive, make it aware
        generated_at = digest.generated_at
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=timezone.utc)
        delta = now - generated_at
        return delta.total_seconds() / 60.0

    # ── Internal ────────────────────────────────────────────────────────────

    def _parse_digest_file(self, path: Path) -> Optional[HermesDigest]:
        """Parse a digest JSON file, returning None on failure."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return HermesDigest(**data)
        except Exception:
            return None
