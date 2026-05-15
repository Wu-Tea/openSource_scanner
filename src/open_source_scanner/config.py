from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from open_source_scanner.models import GitHubSourceConfig, SafetyConfig, ScannerConfig, ScoringConfig


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def load_scanner_config(config_dir: Path = Path("config")) -> ScannerConfig:
    sources = _read_yaml_mapping(config_dir / "sources.yml")
    scoring = _read_yaml_mapping(config_dir / "scoring.yml")
    github_data = sources.get("github", {})
    safety_data = sources.get("safety") or {}
    license_policy = scoring.get("license_policy", {})

    github = GitHubSourceConfig(
        enabled=bool(github_data.get("enabled", False)),
        max_results=int(github_data.get("max_results", 50)),
        repository_queries=list(github_data.get("repository_queries", [])),
        target_keywords=list(github_data.get("target_keywords", [])),
    )
    scoring_config = ScoringConfig(
        weights={key: int(value) for key, value in scoring.get("weights", {}).items()},
        penalties={key: int(value) for key, value in scoring.get("penalties", {}).items()},
        preferred_licenses=set(license_policy.get("preferred", [])),
        caution_licenses=set(license_policy.get("caution", [])),
        packaging_keywords=list(scoring.get("packaging_keywords", [])),
    )
    safety = SafetyConfig(
        max_search_requests_per_run=_int_at_least(
            safety_data.get("max_search_requests_per_run", 10),
            field="safety.max_search_requests_per_run",
            minimum=1,
        ),
        min_seconds_between_requests=_float_at_least(
            safety_data.get("min_seconds_between_requests", 2.0),
            field="safety.min_seconds_between_requests",
            minimum=0.0,
        ),
        rate_limit_remaining_floor=_int_at_least(
            safety_data.get("rate_limit_remaining_floor", 2),
            field="safety.rate_limit_remaining_floor",
            minimum=0,
        ),
        stop_on_rate_limit=_bool_value(
            safety_data.get("stop_on_rate_limit", True),
            field="safety.stop_on_rate_limit",
        ),
    )
    return ScannerConfig(github=github, scoring=scoring_config, safety=safety)


def _int_at_least(value: Any, *, field: str, minimum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer >= {minimum}") from exc
    if parsed < minimum:
        raise ValueError(f"{field} must be >= {minimum}")
    return parsed


def _float_at_least(value: Any, *, field: str, minimum: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number >= {minimum:g}") from exc
    if parsed < minimum:
        raise ValueError(f"{field} must be >= {minimum:g}")
    return parsed


def _bool_value(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise ValueError(f"{field} must be a boolean or one of true/false/yes/no/on/off/1/0")
