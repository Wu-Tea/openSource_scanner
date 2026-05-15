from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from open_source_scanner.models import Opportunity, ScoreBreakdown
from open_source_scanner.storage import OpportunityStore


def _opportunity(
    source_id: str,
    *,
    title: str,
    stars: int,
    signals: list[str] | None = None,
) -> Opportunity:
    return Opportunity(
        source="github",
        source_id=source_id,
        title=title,
        url=f"https://github.com/example/{source_id}",
        description=f"{title} deployment dashboard",
        project=f"example/{source_id}",
        language="Python",
        topics=["ai", "workflow"],
        stars=stars,
        forks=12,
        open_issues=3,
        pushed_at=datetime(2026, 5, 14, 10, 0, tzinfo=UTC),
        archived=False,
        license_spdx_id="mit",
        packaging_signals=signals or ["deploy", "仪表盘"],
    )


def _score(total: int, reason: str = "strong packaging fit") -> ScoreBreakdown:
    return ScoreBreakdown(total=total, reasons=[reason], penalties=[])


def test_initialize_upsert_feedback_and_ranked_listing(tmp_path: Path):
    db_path = tmp_path / "nested" / "scanner.sqlite"
    store = OpportunityStore(db_path)

    store.initialize()

    assert db_path.exists()

    seen_at = datetime(2026, 5, 15, 9, 30, tzinfo=UTC)
    store.upsert_opportunity(_opportunity("low", title="example/low", stars=500), _score(60), seen_at)
    store.upsert_opportunity(
        _opportunity("high", title="example/high", stars=200), _score(90), seen_at
    )
    store.upsert_opportunity(
        _opportunity("tie", title="example/tie", stars=900), _score(90), seen_at
    )

    store.set_feedback("github", "high", "saved")
    store.set_feedback("github", "low", "dismissed")

    second_seen_at = datetime(2026, 5, 15, 11, 0, tzinfo=UTC)
    store.upsert_opportunity(
        _opportunity("high", title="example/high-renamed", stars=700),
        _score(95, "updated score"),
        second_seen_at,
    )

    ranked = store.list_ranked(limit=10)

    assert [row["source_id"] for row in ranked] == ["high", "tie"]
    assert ranked[0]["title"] == "example/high-renamed"
    assert ranked[0]["feedback_status"] == "saved"
    assert ranked[0]["score"] == 95
    assert ranked[0]["first_seen_at"] == seen_at.isoformat()
    assert ranked[0]["last_seen_at"] == second_seen_at.isoformat()
    assert json.loads(ranked[0]["reasons_json"]) == ["updated score"]


def test_upsert_json_encodes_lists_without_ascii_escaping(tmp_path: Path):
    db_path = tmp_path / "scanner.sqlite"
    store = OpportunityStore(db_path)
    store.initialize()

    store.upsert_opportunity(
        _opportunity("unicode", title="example/unicode", stars=100, signals=["部署", "dashboard"]),
        ScoreBreakdown(total=70, reasons=["适合部署"], penalties=["风险低"]),
        datetime(2026, 5, 15, 9, 30, tzinfo=UTC),
    )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT packaging_signals_json, reasons_json, penalties_json
            FROM opportunities
            WHERE source = 'github' AND source_id = 'unicode'
            """
        ).fetchone()

    assert row is not None
    assert "部署" in row[0]
    assert "适合部署" in row[1]
    assert "风险低" in row[2]
