from pathlib import Path

import pytest

from open_source_scanner.config import load_scanner_config


def test_load_scanner_config_reads_sources_and_scoring(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sources.yml").write_text(
        """
github:
  enabled: true
  max_results: 3
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
  keyword_match: 18
penalties:
  unknown_license: -10
license_policy:
  preferred:
    - mit
  caution:
    - agpl-3.0
packaging_keywords:
  - hosted
""",
        encoding="utf-8",
    )

    config = load_scanner_config(config_dir)

    assert config.github.enabled is True
    assert config.github.max_results == 3
    assert config.github.repository_queries == ["topic:ai stars:>10"]
    assert config.github.target_keywords == ["agent"]
    assert config.scoring.weights["keyword_match"] == 18
    assert config.scoring.penalties["unknown_license"] == -10
    assert config.scoring.preferred_licenses == {"mit"}
    assert config.scoring.caution_licenses == {"agpl-3.0"}
    assert config.scoring.packaging_keywords == ["hosted"]
    assert config.safety.max_search_requests_per_run == 10
    assert config.safety.min_seconds_between_requests == 2.0
    assert config.safety.rate_limit_remaining_floor == 2
    assert config.safety.stop_on_rate_limit is True


def test_load_scanner_config_reads_explicit_safety_values(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sources.yml").write_text(
        """
github:
  enabled: true
  max_results: 8
  repository_queries:
    - 'topic:ai stars:>10'
  target_keywords:
    - agent
safety:
  max_search_requests_per_run: 3
  min_seconds_between_requests: 0.25
  rate_limit_remaining_floor: 7
  stop_on_rate_limit: false
""",
        encoding="utf-8",
    )
    (config_dir / "scoring.yml").write_text(
        """
weights: {}
penalties: {}
license_policy:
  preferred: []
  caution: []
packaging_keywords: []
""",
        encoding="utf-8",
    )

    config = load_scanner_config(config_dir)

    assert config.safety.max_search_requests_per_run == 3
    assert config.safety.min_seconds_between_requests == 0.25
    assert config.safety.rate_limit_remaining_floor == 7
    assert config.safety.stop_on_rate_limit is False


def test_load_scanner_config_rejects_invalid_safety_boolean_typo(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _write_sources_with_safety(
        config_dir,
        """
  max_search_requests_per_run: 3
  min_seconds_between_requests: 0.25
  rate_limit_remaining_floor: 7
  stop_on_rate_limit: treu
""",
    )
    _write_minimal_scoring(config_dir)

    with pytest.raises(ValueError, match="safety.stop_on_rate_limit"):
        load_scanner_config(config_dir)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "max_search_requests_per_run",
            "-1",
            "safety.max_search_requests_per_run must be >= 1",
        ),
        (
            "min_seconds_between_requests",
            "-0.1",
            "safety.min_seconds_between_requests must be >= 0",
        ),
        (
            "rate_limit_remaining_floor",
            "-1",
            "safety.rate_limit_remaining_floor must be >= 0",
        ),
    ],
)
def test_load_scanner_config_rejects_negative_safety_values(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    safety_values = {
        "max_search_requests_per_run": "3",
        "min_seconds_between_requests": "0.25",
        "rate_limit_remaining_floor": "7",
        "stop_on_rate_limit": "true",
    }
    safety_values[field] = value
    _write_sources_with_safety(
        config_dir,
        "\n".join(f"  {key}: {item}" for key, item in safety_values.items()),
    )
    _write_minimal_scoring(config_dir)

    with pytest.raises(ValueError, match=message):
        load_scanner_config(config_dir)


def test_load_scanner_config_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sources.yml").write_text("- not-a-mapping\n", encoding="utf-8")
    (config_dir / "scoring.yml").write_text("weights: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sources.yml must contain a YAML mapping"):
        load_scanner_config(config_dir)


def _write_sources_with_safety(config_dir: Path, safety_yaml: str) -> None:
    (config_dir / "sources.yml").write_text(
        f"""
github:
  enabled: true
  max_results: 8
  repository_queries:
    - 'topic:ai stars:>10'
  target_keywords:
    - agent
safety:
{safety_yaml}
""",
        encoding="utf-8",
    )


def _write_minimal_scoring(config_dir: Path) -> None:
    (config_dir / "scoring.yml").write_text(
        """
weights: {}
penalties: {}
license_policy:
  preferred: []
  caution: []
packaging_keywords: []
""",
        encoding="utf-8",
    )
