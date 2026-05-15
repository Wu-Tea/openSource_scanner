from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from open_source_scanner.connectors.github import GitHubConnector


def test_search_repositories_uses_github_search_params_and_maps_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search/repositories"
        assert request.url.params["q"] == "topic:ai stars:>10"
        assert request.url.params["sort"] == "updated"
        assert request.url.params["order"] == "desc"
        assert request.url.params["per_page"] == "1"
        assert request.headers["Accept"] == "application/vnd.github+json"
        assert request.headers["X-GitHub-Api-Version"] == "2022-11-28"
        assert request.headers["Authorization"] == "Bearer test-token"
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 123,
                        "full_name": "demo/agent-kit",
                        "html_url": "https://github.com/demo/agent-kit",
                        "description": "Deployable agent workflow dashboard",
                        "language": "Python",
                        "topics": ["ai", "agent", "workflow"],
                        "stargazers_count": 1200,
                        "forks_count": 90,
                        "open_issues_count": 12,
                        "pushed_at": "2026-05-10T12:30:00Z",
                        "archived": False,
                        "license": {"spdx_id": "MIT"},
                        "owner": {"type": "Organization"},
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client, token="test-token")

    repos = connector.search_repositories("topic:ai stars:>10", limit=1)

    assert len(repos) == 1
    assert repos[0].source == "github"
    assert repos[0].source_id == "123"
    assert repos[0].full_name == "demo/agent-kit"
    assert repos[0].html_url == "https://github.com/demo/agent-kit"
    assert repos[0].description == "Deployable agent workflow dashboard"
    assert repos[0].language == "Python"
    assert repos[0].topics == ["ai", "agent", "workflow"]
    assert repos[0].stars == 1200
    assert repos[0].forks == 90
    assert repos[0].open_issues == 12
    assert repos[0].pushed_at == datetime(2026, 5, 10, 12, 30, tzinfo=UTC)
    assert repos[0].archived is False
    assert repos[0].license_spdx_id == "mit"
    assert repos[0].owner_type == "Organization"
    assert repos[0].raw["id"] == 123


def test_search_repositories_caps_per_page_and_omits_authorization_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["per_page"] == "100"
        assert "Authorization" not in request.headers
        return httpx.Response(200, json={"items": []})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client)

    assert connector.search_repositories("topic:ai", limit=250) == []
    connector.close()
    assert client.is_closed is False
