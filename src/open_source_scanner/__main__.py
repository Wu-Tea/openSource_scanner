from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import httpx
import typer
from rich.console import Console

from open_source_scanner.config import load_scanner_config
from open_source_scanner.connectors.github import GitHubConnector, GitHubConnectorError
from open_source_scanner.memo import write_opportunity_memo
from open_source_scanner.models import FeedbackStatus
from open_source_scanner.normalize import normalize_repository
from open_source_scanner.report import write_report
from open_source_scanner.scoring import score_opportunity
from open_source_scanner.shortlist import write_shortlist
from open_source_scanner.storage import OpportunityStore


app = typer.Typer(help="Scan open-source projects for packaging opportunities.")
console = Console()
FEEDBACK_STATUSES: tuple[FeedbackStatus, ...] = (
    "new",
    "saved",
    "dismissed",
    "watch",
    "package",
)


def _store() -> OpportunityStore:
    db_path = Path(os.getenv("OSS_SCANNER_DB", "data/scanner.sqlite"))
    store = OpportunityStore(db_path)
    store.initialize()
    return store


@app.command()
def scan(
    config_dir: Path = typer.Option(
        Path("config"),
        help="Directory containing sources.yml and scoring.yml.",
    ),
    limit: int = typer.Option(50, min=1, help="Maximum repositories per query."),
) -> None:
    config = load_scanner_config(config_dir)
    store = _store()

    if not config.github.enabled:
        console.print("[yellow]GitHub source is disabled. Enable it in sources.yml to scan.[/yellow]")
        raise typer.Exit()

    now = datetime.now(tz=UTC)
    search_limit = min(limit, config.github.max_results, 100)
    connector = GitHubConnector()
    count = 0

    try:
        for query in config.github.repository_queries:
            repositories = connector.search_repositories(query, limit=search_limit)
            for repository in repositories:
                opportunity = normalize_repository(repository, config.scoring.packaging_keywords)
                score = score_opportunity(opportunity, config.scoring, now=now)
                store.upsert_opportunity(opportunity, score, seen_at=now)
                count += 1
    except GitHubConnectorError as exc:
        console.print(f"[red]GitHub scan failed: {exc}[/red]")
        raise typer.Exit(code=1) from exc
    except httpx.HTTPError as exc:
        console.print(
            "[red]GitHub network error: request failed. "
            "Check network access and GitHub availability.[/red]"
        )
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        console.print("[red]GitHub response could not be processed.[/red]")
        raise typer.Exit(code=1) from exc
    finally:
        connector.close()

    console.print(f"[green]Scanned and stored {count} opportunity observations.[/green]")


@app.command()
def report(
    today: bool = typer.Option(False, help="Use the current UTC date for the report filename."),
    limit: int = typer.Option(20, min=1, help="Number of ranked opportunities to include."),
    output_dir: Path = typer.Option(Path("reports"), help="Report output directory."),
) -> None:
    report_date = datetime.now(tz=UTC).date().isoformat()
    store = _store()
    rows = store.list_ranked(limit=limit)
    output_path = write_report(rows, report_date=report_date, output_dir=output_dir)
    console.print(f"[green]Report written to {output_path}[/green]")


@app.command()
def memo(
    source: str = typer.Argument(..., help="Opportunity source from the report Feedback target."),
    source_id: str = typer.Argument(..., help="Source-specific id from the report Feedback target."),
    output_dir: Path = typer.Option(Path("memos"), help="Memo output directory."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing memo file."),
) -> None:
    memo_date = datetime.now(tz=UTC).date().isoformat()
    store = _store()
    row = store.get_opportunity(source, source_id)
    if row is None:
        console.print(f"[red]No opportunity found for {source}:{source_id}.[/red]")
        raise typer.Exit(code=1)

    try:
        output_path = write_opportunity_memo(
            row,
            memo_date=memo_date,
            output_dir=output_dir,
            force=force,
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}. Re-run with --force to overwrite.[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Memo written to {output_path}[/green]")


@app.command()
def shortlist(
    statuses: str = typer.Option(
        "package,watch,saved",
        help="Comma-separated feedback statuses to include.",
    ),
    limit: int = typer.Option(50, min=1, help="Maximum opportunities to include."),
    output: Path = typer.Option(Path("reports/shortlist.md"), help="Shortlist output path."),
) -> None:
    parsed_statuses = _parse_feedback_statuses(statuses)
    report_date = datetime.now(tz=UTC).date().isoformat()
    store = _store()
    rows = store.list_by_feedback(list(parsed_statuses), limit=limit)
    output_path = write_shortlist(rows, report_date=report_date, output_path=output)
    console.print(f"[green]Shortlist written to {output_path}[/green]")


@app.command()
def feedback(
    source: str = typer.Argument(..., help="Opportunity source, such as github."),
    source_id: str = typer.Argument(..., help="Source-specific opportunity id."),
    status: str = typer.Argument(..., help="new, saved, dismissed, watch, or package."),
) -> None:
    if status not in FEEDBACK_STATUSES:
        console.print(
            "[red]Invalid feedback status. Use one of: "
            f"{', '.join(FEEDBACK_STATUSES)}[/red]"
        )
        raise typer.Exit(code=1)

    store = _store()
    updated = store.set_feedback(source, source_id, cast(FeedbackStatus, status))
    if not updated:
        console.print(f"[red]No opportunity found for {source}:{source_id}.[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]Feedback saved for {source}:{source_id} -> {status}[/green]")


def _parse_feedback_statuses(value: str) -> tuple[FeedbackStatus, ...]:
    statuses = tuple(status.strip() for status in value.split(",") if status.strip())
    invalid_statuses = [status for status in statuses if status not in FEEDBACK_STATUSES]
    if invalid_statuses:
        console.print(
            "[red]Invalid shortlist status. Use one of: "
            f"{', '.join(FEEDBACK_STATUSES)}[/red]"
        )
        raise typer.Exit(code=1)
    return cast(tuple[FeedbackStatus, ...], statuses)


if __name__ == "__main__":
    app()
