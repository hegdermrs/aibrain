#!/usr/bin/env python3
"""
Operations Co-Founder — Brain CLI

Commands:
  brief    Generate daily briefing (morning/evening)
  analyze  Analyze call transcripts
  lens     Pressure-test decisions through strategic personas
  list     List available personas
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from brain.models import (
    BriefingType,
    CallTranscript,
    LensQuery,
)
from brain.briefing import generate_briefing
from brain.analyst import analyze_transcript
from brain.lens import run_lens_parallel
from brain.hermes_interface import HermesInterface
from brain.personas import get_registry

# Rich output if available
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


# ── Shared options ──────────────────────────────────────────────────────────

def _print_json(obj, pretty: bool = True):
    """Print an object as JSON, handling Pydantic models and datetimes."""
    def _serialize(o):
        if hasattr(o, "model_dump"):
            return o.model_dump(mode="json")
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")

    indent = 2 if pretty else None
    print(json.dumps(obj, default=_serialize, indent=indent))


def _print_briefing(briefing):
    """Pretty-print a DailyBriefing."""
    if HAS_RICH:
        emoji = "☀" if briefing.briefing_type == BriefingType.MORNING else "🌙"
        console.print(f"\n[bold]{emoji}  {briefing.headline}[/bold]\n")
        for section in briefing.sections:
            console.print(f"[bold cyan]{section.heading}[/bold cyan]")
            console.print(section.content)
            console.print()
        if briefing.requires_jim_attention:
            console.print("[bold red]⚠ REQUIRES JIM[/bold red]")
            for item in briefing.requires_jim_attention:
                console.print(f"  • {item}")
    else:
        print(f"\n{briefing.headline}\n")
        for section in briefing.sections:
            print(f"{section.heading}")
            print(section.content)
            print()
        if briefing.requires_jim_attention:
            print("⚠ REQUIRES JIM:")
            for item in briefing.requires_jim_attention:
                print(f"  - {item}")


def _print_analysis(analysis):
    """Pretty-print a CallAnalysis."""
    if HAS_RICH:
        console.print(f"\n[bold]{analysis.call_title}[/bold]")
        console.print(f"[dim]{analysis.summary}[/dim]\n")

        if analysis.decisions:
            console.print("[bold green]DECISIONS[/bold green]")
            for d in analysis.decisions:
                console.print(f"  • {d.description}")
            console.print()

        if analysis.follow_ups:
            console.print("[bold yellow]FOLLOW-UPS[/bold yellow]")
            for f in analysis.follow_ups:
                console.print(f"  • {f.description} [dim]({f.owner})[/dim]")
            console.print()

        if analysis.automation_candidates:
            console.print("[bold magenta]DELEGATE / AUTOMATE[/bold magenta]")
            for a in analysis.automation_candidates:
                console.print(f"  • {a.description}")
            console.print()

        if analysis.key_themes:
            console.print("[bold blue]KEY THEMES[/bold blue]")
            for t in analysis.key_themes:
                console.print(f"  • {t}")
    else:
        print(f"\n{analysis.call_title}")
        print(analysis.summary)
        for section_name, items in [
            ("DECISIONS", analysis.decisions),
            ("FOLLOW-UPS", analysis.follow_ups),
            ("DELEGATE/AUTOMATE", analysis.automation_candidates),
            ("KEY THEMES", analysis.key_themes),
        ]:
            if items:
                print(f"\n{section_name}:")
                for item in items:
                    print(f"  - {item.description if hasattr(item, 'description') else item}")


# ── CLI ─────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(version="0.1.0", prog_name="brain")
def cli():
    """
    Operations Co-Founder — Brain

    Pure synthesis and strategy layer for Jim Harshaw Jr.'s coaching business.
    Reads signals surfaced by Hermes. Produces text: briefings, analysis, advice.
    """


# ── brief ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option(
    "--type", "-t",
    "briefing_type",
    type=click.Choice(["morning", "evening"]),
    default="morning",
    help="Morning or evening briefing",
)
@click.option(
    "--digest-dir",
    default=None,
    help="Directory where Hermes drops digests",
)
@click.option(
    "--json", "-j",
    "as_json",
    is_flag=True,
    help="Output as JSON instead of formatted text",
)
def brief(briefing_type: str, digest_dir: str | None, as_json: bool):
    """Generate a daily briefing from Hermes signals."""
    hermes = HermesInterface(digest_dir=digest_dir)
    digest = hermes.read_latest_digest()
    metrics = hermes.read_metrics()

    if digest is None:
        click.secho("No digest found. Has Hermes dropped any data yet?", fg="red")
        sys.exit(1)

    bt = BriefingType.MORNING if briefing_type == "morning" else BriefingType.EVENING

    click.secho("Generating briefing...", fg="yellow")
    result = generate_briefing(
        digest=digest,
        metrics=metrics,
        briefing_type=bt,
    )

    if as_json:
        _print_json(result)
    else:
        _print_briefing(result)

    # Save to file
    out_dir = Path("data/briefings")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out_path = out_dir / f"{briefing_type}_{ts}.json"
    out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
    click.secho(f"Saved to {out_path}", fg="dim")


# ── analyze ────────────────────────────────────────────────────────────────

@cli.command()
@click.option(
    "--transcript-id", "-t",
    default=None,
    help="Transcript ID to analyze (default: latest)",
)
@click.option(
    "--transcript-dir",
    default=None,
    help="Directory with transcript files",
)
@click.option(
    "--file", "-f",
    "file_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to a JSON transcript file",
)
@click.option(
    "--json", "-j",
    "as_json",
    is_flag=True,
    help="Output as JSON",
)
def analyze(transcript_id: str | None, transcript_dir: str | None, file_path: str | None, as_json: bool):
    """Analyze a call transcript and surface decisions, follow-ups, and delegation targets."""
    if file_path:
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        transcript = CallTranscript(**data)
    else:
        hermes = HermesInterface(transcript_dir=transcript_dir)
        if transcript_id:
            transcript = hermes.read_transcript(transcript_id)
        else:
            transcript = hermes.read_latest_transcript()

        if transcript is None:
            click.secho("No transcript found.", fg="red")
            sys.exit(1)

    click.secho(f"Analyzing: {transcript.title}...", fg="yellow")
    result = analyze_transcript(transcript)

    if as_json:
        _print_json(result)
    else:
        _print_analysis(result)

    # Save to file
    out_dir = Path("data/analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out_path = out_dir / f"analysis_{ts}.json"
    out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
    click.secho(f"Saved to {out_path}", fg="dim")


# ── lens ───────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("question")
@click.option(
    "--personas", "-p",
    multiple=True,
    default=None,
    help="Personas to use (repeatable). Default: all available.",
)
@click.option(
    "--context", "-c",
    default="",
    help="Additional context for the question",
)
@click.option(
    "--constraint",
    multiple=True,
    default=None,
    help="Constraints to consider (repeatable)",
)
@click.option(
    "--json", "-j",
    "as_json",
    is_flag=True,
    help="Output as JSON",
)
def lens(
    question: str,
    personas: tuple[str, ...] | None,
    context: str,
    constraint: tuple[str, ...] | None,
    as_json: bool,
):
    """Pressure-test a decision through strategic personas.

    QUESTION is the decision or question to analyze.

    Example:
        brain lens "Should we raise prices?" -p hormozi -p musk -c "Current: $500/mo"
    """
    query = LensQuery(
        question=question,
        context=context,
        personas=list(personas) if personas else [],
        constraints=list(constraint) if constraint else [],
    )

    click.secho(f"Running lens with {len(query.personas) or 'all'} persona(s)...", fg="yellow")
    result = run_lens_parallel(query)

    if as_json:
        _print_json(result)
    else:
        if HAS_RICH:
            console.print(f"\n[bold]Question:[/bold] {question}")
            if context:
                console.print(f"[dim]Context: {context}[/dim]")
            console.print()

            for r in result.persona_responses:
                console.print(Panel(
                    r.analysis,
                    title=f"[bold]{r.persona_name}[/bold]",
                    border_style="cyan",
                ))

            console.print(Panel(
                result.synthesis,
                title="[bold]SYNTHESIS[/bold]",
                border_style="green",
            ))
        else:
            print(f"\nQuestion: {question}")
            for r in result.persona_responses:
                print(f"\n--- {r.persona_name} ---")
                print(r.analysis)
            print(f"\n=== SYNTHESIS ===\n{result.synthesis}")

    # Save to file
    out_dir = Path("data/analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    out_path = out_dir / f"lens_{ts}.json"
    out_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2))
    click.secho(f"Saved to {out_path}", fg="dim")


# ── list ───────────────────────────────────────────────────────────────────

@cli.command("list-personas")
def list_personas():
    """List available strategic personas."""
    registry = get_registry()
    personas = registry.get_all()

    if HAS_RICH:
        table = Table(title="Available Personas")
        table.add_column("Name", style="cyan")
        table.add_column("Tagline")
        for p in personas:
            table.add_row(p.name, p.tagline)
        console.print(table)
    else:
        for p in personas:
            print(f"  {p.name}: {p.tagline}")


if __name__ == "__main__":
    cli()
