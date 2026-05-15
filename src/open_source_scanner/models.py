from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


FeedbackStatus = Literal["new", "saved", "dismissed", "watch", "package"]


@dataclass(frozen=True)
class GitHubSourceConfig:
    enabled: bool
    max_results: int
    repository_queries: list[str]
    target_keywords: list[str]


@dataclass(frozen=True)
class ScoringConfig:
    weights: dict[str, int]
    penalties: dict[str, int]
    preferred_licenses: set[str]
    caution_licenses: set[str]
    packaging_keywords: list[str]


@dataclass(frozen=True)
class ScannerConfig:
    github: GitHubSourceConfig
    scoring: ScoringConfig


@dataclass(frozen=True)
class RawRepository:
    source: Literal["github"]
    source_id: str
    full_name: str
    html_url: str
    description: str
    language: str | None
    topics: list[str]
    stars: int
    forks: int
    open_issues: int
    pushed_at: datetime
    archived: bool
    license_spdx_id: str | None
    owner_type: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Opportunity:
    source: Literal["github"]
    source_id: str
    title: str
    url: str
    description: str
    project: str
    language: str | None
    topics: list[str]
    stars: int
    forks: int
    open_issues: int
    pushed_at: datetime
    archived: bool
    license_spdx_id: str | None
    packaging_signals: list[str]


@dataclass(frozen=True)
class ScoreBreakdown:
    total: int
    reasons: list[str]
    penalties: list[str]
