from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from open_source_scanner.models import FeedbackStatus, Opportunity, ScoreBreakdown


class OpportunityStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS opportunities (
                    source TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT NOT NULL,
                    project TEXT NOT NULL,
                    language TEXT,
                    topics_json TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    forks INTEGER NOT NULL,
                    open_issues INTEGER NOT NULL,
                    pushed_at TEXT NOT NULL,
                    archived INTEGER NOT NULL,
                    license_spdx_id TEXT,
                    packaging_signals_json TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    reasons_json TEXT NOT NULL,
                    penalties_json TEXT NOT NULL,
                    feedback_status TEXT NOT NULL DEFAULT 'new',
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    PRIMARY KEY (source, source_id)
                )
                """
            )

    def upsert_opportunity(
        self,
        opportunity: Opportunity,
        score: ScoreBreakdown,
        seen_at: datetime,
    ) -> None:
        payload = {
            "source": opportunity.source,
            "source_id": opportunity.source_id,
            "title": opportunity.title,
            "url": opportunity.url,
            "description": opportunity.description,
            "project": opportunity.project,
            "language": opportunity.language,
            "topics_json": _encode_list(opportunity.topics),
            "stars": opportunity.stars,
            "forks": opportunity.forks,
            "open_issues": opportunity.open_issues,
            "pushed_at": opportunity.pushed_at.isoformat(),
            "archived": int(opportunity.archived),
            "license_spdx_id": opportunity.license_spdx_id,
            "packaging_signals_json": _encode_list(opportunity.packaging_signals),
            "score": score.total,
            "reasons_json": _encode_list(score.reasons),
            "penalties_json": _encode_list(score.penalties),
            "seen_at": seen_at.isoformat(),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO opportunities (
                    source,
                    source_id,
                    title,
                    url,
                    description,
                    project,
                    language,
                    topics_json,
                    stars,
                    forks,
                    open_issues,
                    pushed_at,
                    archived,
                    license_spdx_id,
                    packaging_signals_json,
                    score,
                    reasons_json,
                    penalties_json,
                    first_seen_at,
                    last_seen_at
                )
                VALUES (
                    :source,
                    :source_id,
                    :title,
                    :url,
                    :description,
                    :project,
                    :language,
                    :topics_json,
                    :stars,
                    :forks,
                    :open_issues,
                    :pushed_at,
                    :archived,
                    :license_spdx_id,
                    :packaging_signals_json,
                    :score,
                    :reasons_json,
                    :penalties_json,
                    :seen_at,
                    :seen_at
                )
                ON CONFLICT(source, source_id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    description = excluded.description,
                    project = excluded.project,
                    language = excluded.language,
                    topics_json = excluded.topics_json,
                    stars = excluded.stars,
                    forks = excluded.forks,
                    open_issues = excluded.open_issues,
                    pushed_at = excluded.pushed_at,
                    archived = excluded.archived,
                    license_spdx_id = excluded.license_spdx_id,
                    packaging_signals_json = excluded.packaging_signals_json,
                    score = excluded.score,
                    reasons_json = excluded.reasons_json,
                    penalties_json = excluded.penalties_json,
                    last_seen_at = excluded.last_seen_at
                """,
                payload,
            )

    def set_feedback(self, source: str, source_id: str, status: FeedbackStatus) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE opportunities
                SET feedback_status = ?
                WHERE source = ? AND source_id = ?
                """,
                (status, source, source_id),
            )
            return cursor.rowcount > 0

    def get_opportunity(self, source: str, source_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM opportunities
                WHERE source = ? AND source_id = ?
                """,
                (source, source_id),
            ).fetchone()
        return dict(row) if row is not None else None

    def list_ranked(self, limit: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM opportunities
                WHERE feedback_status != 'dismissed'
                ORDER BY score DESC, stars DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_by_feedback(self, statuses: list[str], limit: int) -> list[dict[str, Any]]:
        if not statuses:
            return []

        placeholders = ", ".join("?" for _ in statuses)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM opportunities
                WHERE feedback_status IN ({placeholders})
                ORDER BY
                    CASE feedback_status
                        WHEN 'package' THEN 0
                        WHEN 'watch' THEN 1
                        WHEN 'saved' THEN 2
                        WHEN 'new' THEN 3
                        WHEN 'dismissed' THEN 4
                        ELSE 5
                    END,
                    score DESC,
                    stars DESC,
                    title COLLATE NOCASE ASC,
                    source ASC,
                    source_id ASC
                LIMIT ?
                """,
                (*statuses, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn


def _encode_list(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False)
