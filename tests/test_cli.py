from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from open_source_scanner import __main__ as cli
from open_source_scanner.models import RawRepository
from open_source_scanner.storage import OpportunityStore


runner = CliRunner()


def _write_config(config_dir: Path, *, github_enabled: bool = True, max_results: int = 50) -> None:
    config_dir.mkdir()
    (config_dir / "sources.yml").write_text(
        f"""
github:
  enabled: {str(github_enabled).lower()}
  max_results: {max_results}
  repository_queries:
    - 'topic:ai stars:>10'
  target_keywords:
    - agent
""",
        encoding="utf-8",
    )
    (config_dir / "scoring.yml").write_text(
        """
weights:
  repo_popularity: 16
  recent_activity: 14
  packaging_fit: 22
  license_fit: 15
  low_friction: 10
  feedback_bonus: 5
penalties:
  archived_repo: -40
  stale_repo: -25
  restrictive_license: -30
  unknown_license: -10
  weak_description: -8
license_policy:
  preferred:
    - mit
  caution:
    - agpl-3.0
packaging_keywords:
  - deploy
  - dashboard
""",
        encoding="utf-8",
    )


def test_feedback_rejects_invalid_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))

    result = runner.invoke(cli.app, ["feedback", "github", "123", "maybe"])

    assert result.exit_code == 1
    assert "Invalid feedback status" in result.output
    assert "new, saved, dismissed, watch, package" in result.output


def test_report_command_writes_empty_store_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))
    output_dir = tmp_path / "reports"

    result = runner.invoke(cli.app, ["report", "--today", "--output-dir", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert "Report written to" in result.output
    report_files = list(output_dir.glob("*.md"))
    assert len(report_files) == 1
    assert "No opportunities found" in report_files[0].read_text(encoding="utf-8")


def test_scan_exits_when_github_is_disabled(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    _write_config(config_dir, github_enabled=False)
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))

    result = runner.invoke(cli.app, ["scan", "--config-dir", str(config_dir), "--limit", "5"])

    assert result.exit_code == 0, result.output
    assert "GitHub source is disabled" in result.output
    assert db_path.exists()


def test_scan_normalizes_scores_and_stores_fake_github_results(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    _write_config(config_dir, max_results=2)
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))

    class FakeGitHubConnector:
        instances: list[FakeGitHubConnector] = []

        def __init__(self) -> None:
            self.calls: list[tuple[str, int]] = []
            self.closed = False
            self.instances.append(self)

        def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
            self.calls.append((query, limit))
            return [
                RawRepository(
                    source="github",
                    source_id="123",
                    full_name="demo/agent-kit",
                    html_url="https://github.com/demo/agent-kit",
                    description="Deployable agent workflow dashboard",
                    language="Python",
                    topics=["ai", "agent", "workflow"],
                    stars=1200,
                    forks=90,
                    open_issues=12,
                    pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
                    archived=False,
                    license_spdx_id="mit",
                    owner_type="Organization",
                )
            ]

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(cli, "GitHubConnector", FakeGitHubConnector)

    result = runner.invoke(cli.app, ["scan", "--config-dir", str(config_dir), "--limit", "500"])

    assert result.exit_code == 0, result.output
    assert "Scanned and stored 1 opportunity" in result.output
    assert FakeGitHubConnector.instances[0].calls == [("topic:ai stars:>10", 2)]
    assert FakeGitHubConnector.instances[0].closed is True

    store = OpportunityStore(db_path)
    rows = store.list_ranked(limit=10)
    assert rows[0]["source_id"] == "123"
    assert rows[0]["title"] == "demo/agent-kit"
    assert rows[0]["score"] > 0
