from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from open_source_scanner.connectors.github import GitHubConnector, GitHubConnectorError


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
            headers={
                "X-RateLimit-Limit": "30",
                "X-RateLimit-Remaining": "29",
                "X-RateLimit-Reset": "1770000000",
                "X-RateLimit-Used": "1",
                "X-RateLimit-Resource": "search",
            },
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
    assert connector.last_rate_limit_state is not None
    assert connector.last_rate_limit_state.limit == 30
    assert connector.last_rate_limit_state.remaining == 29
    assert connector.last_rate_limit_state.reset == 1770000000
    assert connector.last_rate_limit_state.used == 1
    assert connector.last_rate_limit_state.resource == "search"
    assert connector.last_rate_limit_state.retry_after is None


def test_search_repositories_allows_limit_100_and_omits_authorization_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["per_page"] == "100"
        assert "Authorization" not in request.headers
        return httpx.Response(200, json={"items": []})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client)

    assert connector.search_repositories("topic:ai", limit=100) == []
    connector.close()
    assert client.is_closed is False


@pytest.mark.parametrize("limit", [0, -1])
def test_search_repositories_rejects_limits_below_one(limit: int) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"unexpected request: {request.url}")

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client)

    with pytest.raises(ValueError, match="between 1 and 100"):
        connector.search_repositories("topic:ai", limit=limit)


def test_search_repositories_rejects_limits_above_one_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"unexpected request: {request.url}")

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client)

    with pytest.raises(ValueError, match="between 1 and 100"):
        connector.search_repositories("topic:ai", limit=101)


def test_search_repositories_wraps_rate_limit_errors_with_context() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            json={"message": "API rate limit exceeded for this user."},
            headers={
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1770000000",
                "Retry-After": "60",
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    connector = GitHubConnector(client=client, token="test-token")

    with pytest.raises(GitHubConnectorError) as exc_info:
        connector.search_repositories("topic:ai stars:>10", limit=10)

    error = exc_info.value
    assert error.status_code == 403
    assert error.github_message == "API rate limit exceeded for this user."
    assert error.query == "topic:ai stars:>10"
    assert error.auth_used is True
    assert error.rate_limit_headers == {
        "retry-after": "60",
        "x-ratelimit-limit": "5000",
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": "1770000000",
    }
    assert connector.last_rate_limit_state is not None
    assert connector.last_rate_limit_state.limit == 5000
    assert connector.last_rate_limit_state.remaining == 0
    assert connector.last_rate_limit_state.reset == 1770000000
    assert connector.last_rate_limit_state.retry_after == 60
    assert "GitHub repository search failed" in str(error)
    assert "status 403" in str(error)
    assert "topic:ai stars:>10" in str(error)
    assert "API rate limit exceeded" in str(error)
    assert "authenticated request" in str(error)
    assert "remaining=0" in str(error)
