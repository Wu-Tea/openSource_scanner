from __future__ import annotations

from datetime import UTC, datetime

from open_source_scanner.models import RawRepository
from open_source_scanner.normalize import normalize_repository


def test_normalize_repository_extracts_packaging_signals_in_keyword_order() -> None:
    repo = RawRepository(
        source="github",
        source_id="123",
        full_name="Demo/DeployKit",
        html_url="https://github.com/demo/deploykit",
        description="Hosted workflow dashboard for AI agents",
        language="Python",
        topics=["Docker", "automation"],
        stars=150,
        forks=20,
        open_issues=4,
        pushed_at=datetime(2026, 5, 10, tzinfo=UTC),
        archived=False,
        license_spdx_id="mit",
        owner_type="Organization",
    )

    opportunity = normalize_repository(repo, ["docker", "deploy", "hosted", "api", "workflow"])

    assert opportunity.source == repo.source
    assert opportunity.source_id == repo.source_id
    assert opportunity.title == repo.full_name
    assert opportunity.url == repo.html_url
    assert opportunity.description == repo.description
    assert opportunity.project == repo.full_name
    assert opportunity.language == repo.language
    assert opportunity.topics == repo.topics
    assert opportunity.stars == repo.stars
    assert opportunity.forks == repo.forks
    assert opportunity.open_issues == repo.open_issues
    assert opportunity.pushed_at == repo.pushed_at
    assert opportunity.archived == repo.archived
    assert opportunity.license_spdx_id == repo.license_spdx_id
    assert opportunity.packaging_signals == ["docker", "deploy", "hosted", "workflow"]


def test_normalize_repository_matches_topics_case_insensitively() -> None:
    repo = RawRepository(
        source="github",
        source_id="456",
        full_name="demo/basic-tool",
        html_url="https://github.com/demo/basic-tool",
        description="Small utility",
        language=None,
        topics=["No-Code", "Integrations"],
        stars=20,
        forks=1,
        open_issues=0,
        pushed_at=datetime(2026, 5, 10, tzinfo=UTC),
        archived=False,
        license_spdx_id=None,
        owner_type=None,
    )

    opportunity = normalize_repository(repo, ["integration", "no-code"])

    assert opportunity.packaging_signals == ["integration", "no-code"]
