from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from open_source_scanner.models import GitHubSourceConfig, ScannerConfig, ScoringConfig


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
    return ScannerConfig(github=github, scoring=scoring_config)
