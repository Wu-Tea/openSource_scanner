from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

import httpx

from open_source_scanner.models import RawRepository


GITHUB_API_BASE = "https://api.github.com"
RATE_LIMIT_HEADER_NAMES = {
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "x-ratelimit-resource",
    "x-ratelimit-used",
}


@dataclass(frozen=True)
class GitHubRateLimitState:
    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None
    used: int | None = None
    resource: str | None = None
    retry_after: int | None = None


class GitHubConnectorError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        github_message: str,
        rate_limit_headers: dict[str, str],
        query: str,
        auth_used: bool,
    ) -> None:
        self.status_code = status_code
        self.github_message = github_message
        self.rate_limit_headers = rate_limit_headers
        self.query = query
        self.auth_used = auth_used
        super().__init__(self._human_message())

    def _human_message(self) -> str:
        auth_context = "authenticated request" if self.auth_used else "unauthenticated request"
        message = (
            f"GitHub repository search failed for query {self.query!r} "
            f"with status {self.status_code}: {self.github_message} ({auth_context})"
        )
        rate_context = _format_rate_limit_context(self.rate_limit_headers)
        if rate_context:
            message = f"{message}; {rate_context}"
        return message


class GitHubConnector:
    def __init__(
        self,
        client: httpx.Client | None = None,
        token: str | None = None,
        base_url: str = GITHUB_API_BASE,
    ) -> None:
        self._owns_client = client is None
        resolved_token = token if token is not None else os.getenv("GITHUB_TOKEN")
        self._auth_used = bool(resolved_token)
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if resolved_token:
            self._headers["Authorization"] = f"Bearer {resolved_token}"
        self._client = client or httpx.Client(base_url=base_url, timeout=30.0)
        self.last_rate_limit_state: GitHubRateLimitState | None = None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def search_repositories(self, query: str, limit: int) -> list[RawRepository]:
        if limit < 1 or limit > 100:
            raise ValueError("GitHub repository search limit must be between 1 and 100 for V1")

        response = self._client.get(
            "/search/repositories",
            params={
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": limit,
            },
            headers=self._headers,
        )
        self.last_rate_limit_state = _rate_limit_state(response)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise _github_connector_error(
                response=exc.response,
                query=query,
                auth_used=self._auth_used,
            ) from exc
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


def _github_connector_error(
    *,
    response: httpx.Response,
    query: str,
    auth_used: bool,
) -> GitHubConnectorError:
    return GitHubConnectorError(
        status_code=response.status_code,
        github_message=_github_message(response),
        rate_limit_headers=_rate_limit_headers(response),
        query=query,
        auth_used=auth_used,
    )


def _github_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict) and isinstance(payload.get("message"), str):
        return payload["message"]
    return response.text or response.reason_phrase


def _rate_limit_headers(response: httpx.Response) -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in response.headers.items()
        if key.lower() in RATE_LIMIT_HEADER_NAMES
    }


def _rate_limit_state(response: httpx.Response) -> GitHubRateLimitState:
    headers = _rate_limit_headers(response)
    return GitHubRateLimitState(
        limit=_optional_int_header(headers, "x-ratelimit-limit"),
        remaining=_optional_int_header(headers, "x-ratelimit-remaining"),
        reset=_optional_int_header(headers, "x-ratelimit-reset"),
        used=_optional_int_header(headers, "x-ratelimit-used"),
        resource=headers.get("x-ratelimit-resource"),
        retry_after=_optional_int_header(headers, "retry-after"),
    )


def _optional_int_header(headers: Mapping[str, str], name: str) -> int | None:
    value = headers.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _format_rate_limit_context(rate_limit_headers: dict[str, str]) -> str:
    fields = [
        ("x-ratelimit-remaining", "remaining"),
        ("x-ratelimit-limit", "limit"),
        ("x-ratelimit-reset", "reset"),
        ("x-ratelimit-used", "used"),
        ("x-ratelimit-resource", "resource"),
        ("retry-after", "retry_after"),
    ]
    parts = [
        f"{label}={rate_limit_headers[header]}"
        for header, label in fields
        if header in rate_limit_headers
    ]
    if not parts:
        return ""
    return f"rate limit context: {', '.join(parts)}"
