from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from open_source_scanner.models import RawRepository


GITHUB_API_BASE = "https://api.github.com"


class GitHubConnector:
    def __init__(
        self,
        client: httpx.Client | None = None,
        token: str | None = None,
        base_url: str = GITHUB_API_BASE,
    ) -> None:
        self._owns_client = client is None
        resolved_token = token if token is not None else os.getenv("GITHUB_TOKEN")
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if resolved_token:
            self._headers["Authorization"] = f"Bearer {resolved_token}"
        self._client = client or httpx.Client(base_url=base_url, timeout=30.0)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
        response = self._client.get(
            "/search/repositories",
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": min(limit, 100),
            },
            headers=self._headers,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        if not isinstance(items, list):
            return []
        return [self._map_repository(item) for item in items[:limit] if isinstance(item, dict)]

    @staticmethod
    def _map_repository(item: dict[str, Any]) -> RawRepository:
        license_data = item.get("license") or {}
        owner_data = item.get("owner") or {}
        spdx_id = license_data.get("spdx_id") if isinstance(license_data, dict) else None
        owner_type = owner_data.get("type") if isinstance(owner_data, dict) else None
        pushed_at = datetime.fromisoformat(str(item["pushed_at"]).replace("Z", "+00:00"))

        return RawRepository(
            source="github",
            source_id=str(item["id"]),
            full_name=str(item["full_name"]),
            html_url=str(item["html_url"]),
            description=str(item.get("description") or ""),
            language=item.get("language"),
            topics=list(item.get("topics") or []),
            stars=int(item.get("stargazers_count") or 0),
            forks=int(item.get("forks_count") or 0),
            open_issues=int(item.get("open_issues_count") or 0),
            pushed_at=pushed_at.astimezone(UTC),
            archived=bool(item.get("archived", False)),
            license_spdx_id=str(spdx_id).lower() if spdx_id else None,
            owner_type=str(owner_type) if owner_type else None,
            raw=dict(item),
        )
