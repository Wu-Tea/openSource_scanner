from __future__ import annotations

from datetime import UTC, datetime, timedelta

from open_source_scanner.models import Opportunity, ScoringConfig
from open_source_scanner.scoring import score_opportunity


def _config() -> ScoringConfig:
    return ScoringConfig(
        weights={
            "keyword_match": 18,
            "repo_popularity": 16,
            "recent_activity": 14,
            "packaging_fit": 22,
            "license_fit": 15,
            "low_friction": 10,
            "feedback_bonus": 5,
        },
        penalties={
            "archived_repo": -40,
            "stale_repo": -25,
            "restrictive_license": -30,
            "unknown_license": -10,
            "weak_description": -8,
        },
        preferred_licenses={"mit", "apache-2.0"},
        caution_licenses={"gpl-3.0", "agpl-3.0"},
        packaging_keywords=["deploy", "hosted", "dashboard", "workflow", "api"],
    )


def _opportunity(**overrides: object) -> Opportunity:
    data = {
        "source": "github",
        "source_id": "123",
        "title": "demo/deploy-dashboard",
        "url": "https://github.com/demo/deploy-dashboard",
        "description": "Hosted deployment workflow dashboard for teams",
        "project": "demo/deploy-dashboard",
        "language": "Python",
        "topics": ["workflow", "automation"],
        "stars": 1200,
        "forks": 90,
        "open_issues": 12,
        "pushed_at": datetime(2026, 5, 10, tzinfo=UTC),
        "archived": False,
        "license_spdx_id": "mit",
        "packaging_signals": ["deploy", "hosted", "dashboard"],
    }
    data.update(overrides)
    return Opportunity(**data)  # type: ignore[arg-type]


def test_active_packagable_repo_scores_high_with_explanations() -> None:
    now = datetime(2026, 5, 15, tzinfo=UTC)

    score = score_opportunity(_opportunity(), _config(), now=now, feedback_status="watch")

    assert score.total >= 90
    assert any("packaging keywords" in reason for reason in score.reasons)
    assert any("popular repository" in reason for reason in score.reasons)
    assert any("recent activity" in reason for reason in score.reasons)
    assert any("preferred license" in reason for reason in score.reasons)
    assert any("feedback" in reason for reason in score.reasons)
    assert score.penalties == []


def test_archived_unknown_license_repo_scores_low_with_penalties() -> None:
    now = datetime(2026, 5, 15, tzinfo=UTC)
    opportunity = _opportunity(
        description="Tiny tool",
        stars=42,
        open_issues=88,
        pushed_at=now - timedelta(days=365),
        archived=True,
        license_spdx_id=None,
        packaging_signals=[],
    )

    score = score_opportunity(opportunity, _config(), now=now)

    assert score.total < 20
    assert any("archived" in penalty for penalty in score.penalties)
    assert any("stale" in penalty for penalty in score.penalties)
    assert any("unknown license" in penalty for penalty in score.penalties)
    assert any("weak description" in penalty for penalty in score.penalties)


def test_score_is_clamped_at_zero_for_heavily_penalized_repositories() -> None:
    now = datetime(2026, 5, 15, tzinfo=UTC)
    opportunity = _opportunity(
        title="demo/x",
        description="short",
        project="demo/x",
        topics=[],
        stars=0,
        open_issues=500,
        pushed_at=now - timedelta(days=3650),
        archived=True,
        license_spdx_id="custom",
        packaging_signals=[],
    )

    score = score_opportunity(opportunity, _config(), now=now)

    assert score.total == 0
    assert any("unknown license" in penalty for penalty in score.penalties)
