from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import httpx
from typer.testing import CliRunner

from open_source_scanner import __main__ as cli
from open_source_scanner.models import Opportunity, RawRepository, ScoreBreakdown
from open_source_scanner.storage import OpportunityStore


runner = CliRunner()


def _write_config(
    config_dir: Path,
    *,
    github_enabled: bool = True,
    max_results: int = 50,
    repository_queries: list[str] | None = None,
    safety: dict[str, object] | None = None,
) -> None:
    config_dir.mkdir()
    queries = repository_queries or ["topic:ai stars:>10"]
    queries_yaml = "\n".join(f"    - '{query}'" for query in queries)
    safety_yaml = ""
    if safety is not None:
        stop_on_rate_limit = str(safety["stop_on_rate_limit"]).lower()
        safety_yaml = f"""
safety:
  max_search_requests_per_run: {safety["max_search_requests_per_run"]}
  min_seconds_between_requests: {safety["min_seconds_between_requests"]}
  rate_limit_remaining_floor: {safety["rate_limit_remaining_floor"]}
  stop_on_rate_limit: {stop_on_rate_limit}
"""
    (config_dir / "sources.yml").write_text(
        f"""
github:
  enabled: {str(github_enabled).lower()}
  max_results: {max_results}
  repository_queries:
{queries_yaml}
  target_keywords:
    - agent
{safety_yaml}
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


def _raw_repository(source_id: str = "123") -> RawRepository:
    return RawRepository(
        source="github",
        source_id=source_id,
        full_name=f"demo/agent-kit-{source_id}",
        html_url=f"https://github.com/demo/agent-kit-{source_id}",
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


def test_feedback_rejects_invalid_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))

    result = runner.invoke(cli.app, ["feedback", "github", "123", "maybe"])

    assert result.exit_code == 1
    assert "Invalid feedback status" in result.output
    assert "new, saved, dismissed, watch, package" in result.output


def test_feedback_exits_when_target_does_not_exist(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))

    result = runner.invoke(cli.app, ["feedback", "github", "missing", "package"])

    assert result.exit_code == 1
    assert "No opportunity found for github:missing" in result.output


def test_report_command_writes_empty_store_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))
    output_dir = tmp_path / "reports"

    result = runner.invoke(cli.app, ["report", "--today", "--output-dir", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert "Report written to" in result.output
    report_files = list(output_dir.glob("*.md"))
    assert len(report_files) == 1
    assert "No opportunities found" in report_files[0].read_text(encoding="utf-8")


def test_report_command_defaults_to_balanced_category_output(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    seen_at = datetime(2026, 5, 15, 9, 30, tzinfo=UTC)
    rows = [
        ("ai-1", "demo/agent-one", "Agent workflow platform", ["ai", "agent"], 100),
        ("ai-2", "demo/agent-two", "LLM automation dashboard", ["llm", "agent"], 99),
        (
            "infra-1",
            "demo/kube-deploy",
            "Self-hosted Kubernetes deployment dashboard",
            ["kubernetes", "docker"],
            70,
        ),
    ]
    for source_id, title, description, topics, score in rows:
        store.upsert_opportunity(
            Opportunity(
                source="github",
                source_id=source_id,
                title=title,
                url=f"https://github.com/{title}",
                description=description,
                project=title,
                language="Python",
                topics=topics,
                stars=1000,
                forks=90,
                open_issues=12,
                pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
                archived=False,
                license_spdx_id="mit",
                packaging_signals=["deploy", "dashboard"],
            ),
            ScoreBreakdown(total=score, reasons=["test score"], penalties=[]),
            seen_at=seen_at,
        )
    output_dir = tmp_path / "reports"

    result = runner.invoke(
        cli.app,
        [
            "report",
            "--today",
            "--limit",
            "3",
            "--per-category",
            "1",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    report_text = next(output_dir.glob("*.md")).read_text(encoding="utf-8")
    assert report_text.index("demo/agent-one") < report_text.index("demo/kube-deploy")
    assert report_text.index("demo/kube-deploy") < report_text.index("demo/agent-two")


def test_report_command_vertical_focus_prioritizes_business_pain_points(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    seen_at = datetime(2026, 5, 19, 9, 30, tzinfo=UTC)
    rows = [
        (
            "framework",
            "demo/react-starter",
            "React web framework starter with components and frontend templates",
            ["react", "frontend", "web-framework"],
            90,
            50000,
        ),
        (
            "restaurant",
            "demo/restaurant-booking",
            "Restaurant online ordering, table reservation, menu, billing, and staff dashboard",
            ["restaurant-management", "booking-system"],
            61,
            80,
        ),
    ]
    for source_id, title, description, topics, score, stars in rows:
        store.upsert_opportunity(
            Opportunity(
                source="github",
                source_id=source_id,
                title=title,
                url=f"https://github.com/{title}",
                description=description,
                project=title,
                language="TypeScript",
                topics=topics,
                stars=stars,
                forks=10,
                open_issues=3,
                pushed_at=datetime(2026, 5, 18, 12, 30, tzinfo=UTC),
                archived=False,
                license_spdx_id="mit",
                packaging_signals=["template", "dashboard"],
            ),
            ScoreBreakdown(total=score, reasons=["test score"], penalties=[]),
            seen_at=seen_at,
        )
    output_dir = tmp_path / "reports"

    result = runner.invoke(
        cli.app,
        [
            "report",
            "--focus",
            "vertical",
            "--limit",
            "2",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    report_text = next(output_dir.glob("*.md")).read_text(encoding="utf-8")
    assert report_text.index("demo/restaurant-booking") < report_text.index("demo/react-starter")
    assert "Category: Vertical: Restaurant / Hospitality" in report_text


def test_shortlist_command_writes_feedback_pipeline_report(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    store.upsert_opportunity(
        Opportunity(
            source="github",
            source_id="123",
            title="demo/agent-kit",
            url="https://github.com/demo/agent-kit",
            description="Deployable agent workflow dashboard",
            project="demo/agent-kit",
            language="Python",
            topics=["ai", "agent"],
            stars=1200,
            forks=90,
            open_issues=12,
            pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
            archived=False,
            license_spdx_id="mit",
            packaging_signals=["deploy", "dashboard"],
        ),
        ScoreBreakdown(total=88, reasons=["preferred license: mit"], penalties=[]),
        seen_at=datetime(2026, 5, 15, 9, 30, tzinfo=UTC),
    )
    assert store.set_feedback("github", "123", "package") is True
    output_path = tmp_path / "reports" / "shortlist.md"

    result = runner.invoke(cli.app, ["shortlist", "--output", str(output_path)])

    assert result.exit_code == 0, result.output
    assert "Shortlist written to" in result.output
    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "demo/agent-kit" in text
    assert "Feedback target: github 123" in text
    assert "create or review memo" in text


def test_shortlist_rejects_invalid_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))
    output_path = tmp_path / "reports" / "shortlist.md"

    result = runner.invoke(
        cli.app,
        ["shortlist", "--statuses", "package,maybe", "--output", str(output_path)],
    )

    assert result.exit_code == 1
    assert "Invalid shortlist status" in result.output
    assert "new, saved, dismissed, watch, package" in result.output
    assert not output_path.exists()


def test_shortlist_rejects_empty_status_value(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))
    output_path = tmp_path / "reports" / "shortlist.md"

    result = runner.invoke(cli.app, ["shortlist", "--statuses", "", "--output", str(output_path)])

    assert result.exit_code == 1
    assert "No shortlist statuses provided" in result.output
    assert not output_path.exists()


def test_shortlist_rejects_comma_only_statuses(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))
    output_path = tmp_path / "reports" / "shortlist.md"

    result = runner.invoke(
        cli.app,
        ["shortlist", "--statuses", " , ", "--output", str(output_path)],
    )

    assert result.exit_code == 1
    assert "No shortlist statuses provided" in result.output
    assert not output_path.exists()


def test_shortlist_normalizes_statuses_to_lowercase(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    store.upsert_opportunity(
        Opportunity(
            source="github",
            source_id="123",
            title="demo/agent-kit",
            url="https://github.com/demo/agent-kit",
            description="Deployable agent workflow dashboard",
            project="demo/agent-kit",
            language="Python",
            topics=["ai", "agent"],
            stars=1200,
            forks=90,
            open_issues=12,
            pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
            archived=False,
            license_spdx_id="mit",
            packaging_signals=["deploy", "dashboard"],
        ),
        ScoreBreakdown(total=88, reasons=["preferred license: mit"], penalties=[]),
        seen_at=datetime(2026, 5, 15, 9, 30, tzinfo=UTC),
    )
    assert store.set_feedback("github", "123", "package") is True
    output_path = tmp_path / "reports" / "shortlist.md"

    result = runner.invoke(
        cli.app,
        ["shortlist", "--statuses", "Package,Watch", "--output", str(output_path)],
    )

    assert result.exit_code == 0, result.output
    assert "demo/agent-kit" in output_path.read_text(encoding="utf-8")


def test_memo_command_writes_existing_opportunity(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    store.upsert_opportunity(
        Opportunity(
            source="github",
            source_id="123",
            title="demo/agent-kit",
            url="https://github.com/demo/agent-kit",
            description="Deployable agent workflow dashboard",
            project="demo/agent-kit",
            language="Python",
            topics=["ai", "agent"],
            stars=1200,
            forks=90,
            open_issues=12,
            pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
            archived=False,
            license_spdx_id="mit",
            packaging_signals=["deploy", "dashboard"],
        ),
        ScoreBreakdown(total=88, reasons=["preferred license: mit"], penalties=[]),
        seen_at=datetime(2026, 5, 15, 9, 30, tzinfo=UTC),
    )
    output_dir = tmp_path / "memos"

    result = runner.invoke(cli.app, ["memo", "github", "123", "--output-dir", str(output_dir)])

    assert result.exit_code == 0, result.output
    assert "Memo written to" in result.output
    memo_files = list(output_dir.glob("*.md"))
    assert len(memo_files) == 1
    memo_text = memo_files[0].read_text(encoding="utf-8")
    assert "反馈目标: github 123" in memo_text
    assert "## 包装假设" in memo_text


def test_memo_command_requires_force_to_overwrite_existing_memo(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    store = OpportunityStore(db_path)
    store.initialize()
    store.upsert_opportunity(
        Opportunity(
            source="github",
            source_id="123",
            title="demo/agent-kit",
            url="https://github.com/demo/agent-kit",
            description="Deployable agent workflow dashboard",
            project="demo/agent-kit",
            language="Python",
            topics=["ai", "agent"],
            stars=1200,
            forks=90,
            open_issues=12,
            pushed_at=datetime(2026, 5, 10, 12, 30, tzinfo=UTC),
            archived=False,
            license_spdx_id="mit",
            packaging_signals=["deploy", "dashboard"],
        ),
        ScoreBreakdown(total=88, reasons=["preferred license: mit"], penalties=[]),
        seen_at=datetime(2026, 5, 15, 9, 30, tzinfo=UTC),
    )
    output_dir = tmp_path / "memos"

    first = runner.invoke(cli.app, ["memo", "github", "123", "--output-dir", str(output_dir)])
    assert first.exit_code == 0, first.output

    memo_path = next(output_dir.glob("*.md"))
    memo_path.write_text("human edits", encoding="utf-8")
    second = runner.invoke(cli.app, ["memo", "github", "123", "--output-dir", str(output_dir)])

    assert second.exit_code == 1
    assert "Memo already exists" in second.output
    assert memo_path.read_text(encoding="utf-8") == "human edits"

    forced = runner.invoke(
        cli.app,
        ["memo", "github", "123", "--output-dir", str(output_dir), "--force"],
    )

    assert forced.exit_code == 0, forced.output
    assert "Memo written to" in forced.output
    assert memo_path.read_text(encoding="utf-8").startswith("# 机会备忘录 - demo/agent-kit")


def test_memo_command_exits_when_target_does_not_exist(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OSS_SCANNER_DB", str(tmp_path / "scanner.sqlite"))

    result = runner.invoke(cli.app, ["memo", "github", "missing"])

    assert result.exit_code == 1
    assert "No opportunity found for github:missing" in result.output


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


def test_scan_stops_before_exceeding_max_search_request_override(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    queries = ["topic:one", "topic:two", "topic:three"]
    _write_config(
        config_dir,
        repository_queries=queries,
        safety={
            "max_search_requests_per_run": 10,
            "min_seconds_between_requests": 0,
            "rate_limit_remaining_floor": 0,
            "stop_on_rate_limit": False,
        },
    )
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    monkeypatch.setattr(cli, "sleep", lambda seconds: None, raising=False)

    class FakeGitHubConnector:
        instances: list[FakeGitHubConnector] = []

        def __init__(self) -> None:
            self.calls: list[str] = []
            self.last_rate_limit_state = SimpleNamespace(remaining=50)
            self.instances.append(self)

        def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
            self.calls.append(query)
            return []

        def close(self) -> None:
            pass

    monkeypatch.setattr(cli, "GitHubConnector", FakeGitHubConnector)

    result = runner.invoke(
        cli.app,
        [
            "scan",
            "--config-dir",
            str(config_dir),
            "--limit",
            "5",
            "--max-search-requests",
            "2",
        ],
    )

    assert result.exit_code == 0, result.output
    assert FakeGitHubConnector.instances[0].calls == queries[:2]
    assert "Stopped early" in result.output
    assert "request budget" in result.output
    assert "Scanned and stored 0 opportunity observations" in result.output


def test_scan_stops_after_response_when_rate_limit_floor_is_reached(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    queries = ["topic:one", "topic:two", "topic:three"]
    _write_config(
        config_dir,
        repository_queries=queries,
        safety={
            "max_search_requests_per_run": 10,
            "min_seconds_between_requests": 0,
            "rate_limit_remaining_floor": 2,
            "stop_on_rate_limit": True,
        },
    )
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    monkeypatch.setattr(cli, "sleep", lambda seconds: None, raising=False)

    class FakeGitHubConnector:
        instances: list[FakeGitHubConnector] = []

        def __init__(self) -> None:
            self.calls: list[str] = []
            self.last_rate_limit_state = None
            self.instances.append(self)

        def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
            self.calls.append(query)
            self.last_rate_limit_state = SimpleNamespace(
                limit=30,
                remaining=1,
                reset=1770000000,
                used=29,
                resource="search",
                retry_after=None,
            )
            return [_raw_repository()]

        def close(self) -> None:
            pass

    monkeypatch.setattr(cli, "GitHubConnector", FakeGitHubConnector)

    result = runner.invoke(cli.app, ["scan", "--config-dir", str(config_dir), "--limit", "5"])

    assert result.exit_code == 0, result.output
    assert FakeGitHubConnector.instances[0].calls == queries[:1]
    assert "Stopped early" in result.output
    assert "rate limit" in result.output
    assert "remaining=1" in result.output
    assert "Scanned and stored 1 opportunity observation" in result.output
    rows = OpportunityStore(db_path).list_ranked(limit=10)
    assert [row["source_id"] for row in rows] == ["123"]


def test_scan_sleeps_between_search_requests_but_not_before_first(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    queries = ["topic:one", "topic:two", "topic:three"]
    _write_config(
        config_dir,
        repository_queries=queries,
        safety={
            "max_search_requests_per_run": 10,
            "min_seconds_between_requests": 99,
            "rate_limit_remaining_floor": 0,
            "stop_on_rate_limit": False,
        },
    )
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))
    sleep_calls: list[float] = []
    monkeypatch.setattr(cli, "sleep", sleep_calls.append, raising=False)

    class FakeGitHubConnector:
        instances: list[FakeGitHubConnector] = []

        def __init__(self) -> None:
            self.calls: list[str] = []
            self.last_rate_limit_state = SimpleNamespace(remaining=50)
            self.instances.append(self)

        def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
            self.calls.append(query)
            return []

        def close(self) -> None:
            pass

    monkeypatch.setattr(cli, "GitHubConnector", FakeGitHubConnector)

    result = runner.invoke(
        cli.app,
        [
            "scan",
            "--config-dir",
            str(config_dir),
            "--limit",
            "5",
            "--min-seconds-between-requests",
            "0.25",
        ],
    )

    assert result.exit_code == 0, result.output
    assert FakeGitHubConnector.instances[0].calls == queries
    assert sleep_calls == [0.25, 0.25]


def test_scan_handles_network_errors_without_leaking_request_url(
    tmp_path: Path, monkeypatch
) -> None:
    db_path = tmp_path / "scanner.sqlite"
    config_dir = tmp_path / "config"
    _write_config(config_dir)
    monkeypatch.setenv("OSS_SCANNER_DB", str(db_path))

    class FailingGitHubConnector:
        def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
            request = httpx.Request(
                "GET",
                "https://api.github.com/search/repositories?access_token=secret-token",
            )
            raise httpx.RequestError("connection failed", request=request)

        def close(self) -> None:
            pass

    monkeypatch.setattr(cli, "GitHubConnector", FailingGitHubConnector)

    result = runner.invoke(cli.app, ["scan", "--config-dir", str(config_dir), "--limit", "5"])

    assert result.exit_code == 1
    assert "GitHub network error" in result.output
    assert "secret-token" not in result.output
    assert "access_token" not in result.output
