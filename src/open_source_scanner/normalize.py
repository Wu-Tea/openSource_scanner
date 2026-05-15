from __future__ import annotations

from open_source_scanner.models import Opportunity, RawRepository


def normalize_repository(repo: RawRepository, packaging_keywords: list[str]) -> Opportunity:
    searchable_text = " ".join([repo.full_name, repo.description, *repo.topics]).casefold()
    packaging_signals = [
        keyword for keyword in packaging_keywords if keyword.casefold() in searchable_text
    ]

    return Opportunity(
        source=repo.source,
        source_id=repo.source_id,
        title=repo.full_name,
        url=repo.html_url,
        description=repo.description,
        project=repo.full_name,
        language=repo.language,
        topics=repo.topics,
        stars=repo.stars,
        forks=repo.forks,
        open_issues=repo.open_issues,
        pushed_at=repo.pushed_at,
        archived=repo.archived,
        license_spdx_id=repo.license_spdx_id,
        packaging_signals=packaging_signals,
    )
