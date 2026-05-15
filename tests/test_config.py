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


def test_load_scanner_config_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sources.yml").write_text("- not-a-mapping\n", encoding="utf-8")
    (config_dir / "scoring.yml").write_text("weights: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sources.yml must contain a YAML mapping"):
        load_scanner_config(config_dir)
