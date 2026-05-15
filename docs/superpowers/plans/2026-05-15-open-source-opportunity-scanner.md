# Open Source Opportunity Scanner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first scanner that regularly finds open-source projects with packaging and monetization potential, scores them, deduplicates them, and produces actionable Markdown reports.

**Architecture:** The first version is a Python CLI pipeline: configuration defines scan sources, a GitHub connector fetches candidate repositories, a normalizer converts raw data into a common `Opportunity` model, a scoring engine explains why each item is valuable, SQLite stores history and feedback, and a report generator writes daily Markdown reports. The system starts with GitHub only, then leaves clean connector boundaries for Hacker News, Reddit, Product Hunt, Hugging Face, npm, and PyPI.

**Tech Stack:** Python 3.12, uv, Typer, HTTPX, PyYAML, SQLite, pytest, ruff, GitHub REST API.

---

## Application Overview

This project is an "open-source opportunity radar". It helps the user discover projects that can be legally and ethically packaged into something more useful for a specific audience: hosted services, templates, deployment kits, Chinese-localized versions, workflow integrations, training material, or paid support.

The user should picture a daily funnel. The scanner collects raw community signals, turns them into structured candidates, scores each candidate for monetization potential, generates a short report, and lets the user mark items as `saved`, `dismissed`, `watch`, or `package`. The feedback becomes local data so future scoring can be tuned around the user's taste.

The first working outcome is a command that can be run manually or on a schedule:

```powershell
uv run oss-scan scan --limit 50
uv run oss-scan report --today
```

The expected output is a Markdown report under `reports/YYYY-MM-DD.md` with ranked opportunities and clear reasons.

## Current Situation

The repository at `E:\AI\resp_scanner` is a fresh clone of `https://github.com/Wu-Tea/openSource_scanner.git`. It has no committed files yet. That makes the first implementation straightforward: create the project skeleton, define the domain model, implement GitHub scanning, add scoring, persist results, then generate reports.

Important assumptions:

- The first version is local-first and does not require a hosted backend.
- GitHub is the only scan source for the MVP.
- The scanner stores only public project metadata and user feedback.
- Secrets such as `GITHUB_TOKEN` live in `.env` or the shell environment and are never committed.
- Monetization checks must include license risk, not just popularity.

## Proposed Direction

Use a small, testable CLI before building dashboards or complex automations. A CLI keeps the workflow easy to run from Codex, Windows Task Scheduler, GitHub Actions, or a future web UI.

The MVP should answer four questions for every candidate:

1. Is this project active enough to matter?
2. Does it appear to solve a painful or repeated user problem?
3. Can it be packaged into a product, service, template, or support offer?
4. Is there any obvious license or maintenance risk?

The first release should avoid LLM-based judgment. Use explainable scoring rules so bad recommendations can be corrected by editing `config/scoring.yml`. Add LLM summaries only after the data pipeline is stable.

## File Structure

Create this structure during implementation:

```text
.
├── .env.example
├── .github/
│   └── workflows/
│       └── daily-scan.yml
├── .gitignore
├── README.md
├── config/
│   ├── scoring.yml
│   └── sources.yml
├── data/
│   └── .gitkeep
├── docs/
│   ├── opportunity-workflow.md
│   └── superpowers/
│       └── plans/
│           └── 2026-05-15-open-source-opportunity-scanner.md
├── pyproject.toml
├── reports/
│   └── .gitkeep
├── src/
│   └── open_source_scanner/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── models.py
│       ├── normalize.py
│       ├── report.py
│       ├── scoring.py
│       ├── storage.py
│       └── connectors/
│           ├── __init__.py
│           └── github.py
└── tests/
    ├── test_config.py
    ├── test_github_connector.py
    ├── test_report.py
    ├── test_scoring.py
    └── test_storage.py
```

### Responsibility Map

- `config/sources.yml`: scan queries, source enablement, result limits, target topics.
- `config/scoring.yml`: weights, penalties, license policy, packaging keywords.
- `src/open_source_scanner/models.py`: shared dataclasses and enums.
- `src/open_source_scanner/config.py`: load YAML config and environment settings.
- `src/open_source_scanner/connectors/github.py`: call GitHub API and return raw repo candidates.
- `src/open_source_scanner/normalize.py`: convert connector output into `Opportunity` objects.
- `src/open_source_scanner/scoring.py`: compute score and explanation.
- `src/open_source_scanner/storage.py`: SQLite schema, upsert, feedback, query history.
- `src/open_source_scanner/report.py`: render daily Markdown reports.
- `src/open_source_scanner/__main__.py`: Typer CLI commands.
- `.github/workflows/daily-scan.yml`: optional scheduled GitHub Actions run.

---

## Task 1: Scaffold Project

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `data/.gitkeep`
- Create: `reports/.gitkeep`
- Create: `src/open_source_scanner/__init__.py`
- Create: `src/open_source_scanner/connectors/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "open-source-scanner"
version = "0.1.0"
description = "Scan open-source communities for packaging and monetization opportunities."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27.0",
    "pyyaml>=6.0.1",
    "rich>=13.7.1",
    "typer>=0.12.3",
]

[project.scripts]
oss-scan = "open_source_scanner.__main__:app"

[dependency-groups]
dev = [
    "pytest>=8.2.0",
    "ruff>=0.4.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.env
data/*.sqlite
data/*.sqlite-shm
data/*.sqlite-wal
reports/*.tmp
```

- [ ] **Step 3: Create `.env.example`**

```bash
GITHUB_TOKEN=
OSS_SCANNER_DB=data/scanner.sqlite
```

- [ ] **Step 4: Create initial `README.md`**

```markdown
# openSource_scanner

Open-source opportunity radar for finding projects that can be packaged into useful products, services, templates, integrations, or support offers.

## First workflow

1. Scan GitHub for candidate repositories.
2. Normalize public metadata into opportunity records.
3. Score each record with explainable packaging and monetization signals.
4. Store history and feedback in SQLite.
5. Generate a Markdown report under `reports/`.

## Local setup

```powershell
uv sync
$env:GITHUB_TOKEN="your_token"
uv run oss-scan scan --limit 50
uv run oss-scan report --today
```

The token is optional for small manual runs, but recommended to avoid low API rate limits.
```

- [ ] **Step 5: Create keep files and package markers**

Create empty files:

```text
data/.gitkeep
reports/.gitkeep
src/open_source_scanner/__init__.py
src/open_source_scanner/connectors/__init__.py
```

- [ ] **Step 6: Install dependencies**

Run:

```powershell
uv sync
```

Expected:

```text
Resolved ...
Installed ...
```

- [ ] **Step 7: Verify CLI package is importable**

Run:

```powershell
uv run python -c "import open_source_scanner; print(open_source_scanner.__name__)"
```

Expected:

```text
open_source_scanner
```

- [ ] **Step 8: Commit scaffold**

```powershell
git add pyproject.toml .gitignore .env.example README.md data/.gitkeep reports/.gitkeep src/open_source_scanner
git commit -m "chore: scaffold scanner project"
```

---

## Task 2: Add Config Files and Domain Models

**Files:**
- Create: `config/sources.yml`
- Create: `config/scoring.yml`
- Create: `src/open_source_scanner/models.py`
- Create: `src/open_source_scanner/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Create `config/sources.yml`**

```yaml
github:
  enabled: true
  max_results: 50
  repository_queries:
    - 'topic:ai stars:>100 pushed:>2026-01-01'
    - 'topic:automation stars:>50 pushed:>2026-01-01'
    - 'topic:rag stars:>50 pushed:>2026-01-01'
    - 'topic:mcp stars:>20 pushed:>2026-01-01'
    - 'topic:self-hosted stars:>100 pushed:>2026-01-01'
  target_keywords:
    - agent
    - automation
    - deploy
    - hosted
    - rag
    - mcp
    - workflow
    - scraper
    - dashboard
```

- [ ] **Step 2: Create `config/scoring.yml`**

```yaml
weights:
  keyword_match: 18
  repo_popularity: 16
  recent_activity: 14
  packaging_fit: 22
  license_fit: 15
  low_friction: 10
  feedback_bonus: 5

penalties:
  archived_repo: -40
  stale_repo: -25
  restrictive_license: -30
  unknown_license: -10
  weak_description: -8

license_policy:
  preferred:
    - mit
    - apache-2.0
    - bsd-2-clause
    - bsd-3-clause
  caution:
    - gpl-2.0
    - gpl-3.0
    - agpl-3.0
    - lgpl-2.1
    - lgpl-3.0

packaging_keywords:
  - deploy
  - hosted
  - cloud
  - dashboard
  - template
  - plugin
  - integration
  - no-code
  - workflow
  - api
  - docker
```

- [ ] **Step 3: Write failing config tests**

```python
# tests/test_config.py
from pathlib import Path

from open_source_scanner.config import load_scanner_config


def test_load_scanner_config_reads_sources_and_scoring(tmp_path: Path):
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
```

- [ ] **Step 4: Run config test to verify it fails**

Run:

```powershell
uv run pytest tests/test_config.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.config'
```

- [ ] **Step 5: Implement `models.py`**

```python
# src/open_source_scanner/models.py
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
```

- [ ] **Step 6: Implement `config.py`**

```python
# src/open_source_scanner/config.py
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from open_source_scanner.models import GitHubSourceConfig, ScannerConfig, ScoringConfig


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def load_scanner_config(config_dir: Path = Path("config")) -> ScannerConfig:
    sources = _read_yaml(config_dir / "sources.yml")
    scoring = _read_yaml(config_dir / "scoring.yml")
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
```

- [ ] **Step 7: Run config test to verify it passes**

Run:

```powershell
uv run pytest tests/test_config.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 8: Commit config and model foundation**

```powershell
git add config src/open_source_scanner/models.py src/open_source_scanner/config.py tests/test_config.py
git commit -m "feat: add scanner configuration model"
```

---

## Task 3: Implement GitHub Repository Connector

**Files:**
- Create: `src/open_source_scanner/connectors/github.py`
- Create: `tests/test_github_connector.py`

- [ ] **Step 1: Write failing GitHub connector test**

```python
# tests/test_github_connector.py
from datetime import UTC, datetime

import httpx

from open_source_scanner.connectors.github import GitHubConnector


def test_search_repositories_maps_github_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search/repositories"
        assert request.url.params["q"] == "topic:ai stars:>10"
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
    connector = GitHubConnector(client=client)

    repos = connector.search_repositories("topic:ai stars:>10", limit=1)

    assert len(repos) == 1
    assert repos[0].source == "github"
    assert repos[0].source_id == "123"
    assert repos[0].full_name == "demo/agent-kit"
    assert repos[0].stars == 1200
    assert repos[0].license_spdx_id == "mit"
    assert repos[0].pushed_at == datetime(2026, 5, 10, 12, 30, tzinfo=UTC)
```

- [ ] **Step 2: Run GitHub connector test to verify it fails**

Run:

```powershell
uv run pytest tests/test_github_connector.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.connectors.github'
```

- [ ] **Step 3: Implement GitHub connector**

```python
# src/open_source_scanner/connectors/github.py
from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from open_source_scanner.models import RawRepository


GITHUB_API_BASE = "https://api.github.com"


class GitHubConnector:
    def __init__(self, client: httpx.Client | None = None, token: str | None = None) -> None:
        self._owns_client = client is None
        resolved_token = token if token is not None else os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if resolved_token:
            headers["Authorization"] = f"Bearer {resolved_token}"
        self._client = client or httpx.Client(base_url=GITHUB_API_BASE, headers=headers, timeout=30.0)

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
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        if not isinstance(items, list):
            return []
        return [self._map_repository(item) for item in items[:limit]]

    @staticmethod
    def _map_repository(item: dict[str, Any]) -> RawRepository:
        license_data = item.get("license") or {}
        owner_data = item.get("owner") or {}
        spdx_id = license_data.get("spdx_id")
        pushed_at = datetime.fromisoformat(str(item["pushed_at"]).replace("Z", "+00:00")).astimezone(UTC)
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
            pushed_at=pushed_at,
            archived=bool(item.get("archived", False)),
            license_spdx_id=str(spdx_id).lower() if spdx_id else None,
            owner_type=owner_data.get("type"),
            raw=item,
        )
```

- [ ] **Step 4: Run GitHub connector test to verify it passes**

Run:

```powershell
uv run pytest tests/test_github_connector.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit GitHub connector**

```powershell
git add src/open_source_scanner/connectors/github.py tests/test_github_connector.py
git commit -m "feat: add github repository connector"
```

---

## Task 4: Normalize Repositories Into Opportunities

**Files:**
- Create: `src/open_source_scanner/normalize.py`
- Create: `tests/test_normalize.py`

- [ ] **Step 1: Write failing normalization test**

```python
# tests/test_normalize.py
from datetime import UTC, datetime

from open_source_scanner.models import RawRepository
from open_source_scanner.normalize import normalize_repository


def test_normalize_repository_extracts_packaging_signals():
    repo = RawRepository(
        source="github",
        source_id="123",
        full_name="demo/agent-kit",
        html_url="https://github.com/demo/agent-kit",
        description="Deployable agent workflow dashboard with Docker support",
        language="Python",
        topics=["ai", "agent", "workflow"],
        stars=1200,
        forks=90,
        open_issues=12,
        pushed_at=datetime(2026, 5, 10, tzinfo=UTC),
        archived=False,
        license_spdx_id="mit",
        owner_type="Organization",
    )

    opportunity = normalize_repository(repo, packaging_keywords=["deploy", "dashboard", "docker"])

    assert opportunity.title == "demo/agent-kit"
    assert opportunity.project == "demo/agent-kit"
    assert opportunity.packaging_signals == ["deploy", "dashboard", "docker"]
```

- [ ] **Step 2: Run normalization test to verify it fails**

Run:

```powershell
uv run pytest tests/test_normalize.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.normalize'
```

- [ ] **Step 3: Implement normalizer**

```python
# src/open_source_scanner/normalize.py
from __future__ import annotations

from open_source_scanner.models import Opportunity, RawRepository


def normalize_repository(repo: RawRepository, packaging_keywords: list[str]) -> Opportunity:
    searchable = " ".join([repo.full_name, repo.description, " ".join(repo.topics)]).lower()
    signals = [keyword for keyword in packaging_keywords if keyword.lower() in searchable]
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
        packaging_signals=signals,
    )
```

- [ ] **Step 4: Run normalization test to verify it passes**

Run:

```powershell
uv run pytest tests/test_normalize.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit normalizer**

```powershell
git add src/open_source_scanner/normalize.py tests/test_normalize.py
git commit -m "feat: normalize repositories into opportunities"
```

---

## Task 5: Implement Explainable Scoring

**Files:**
- Create: `src/open_source_scanner/scoring.py`
- Create: `tests/test_scoring.py`

- [ ] **Step 1: Write failing scoring tests**

```python
# tests/test_scoring.py
from datetime import UTC, datetime

from open_source_scanner.models import Opportunity, ScoringConfig
from open_source_scanner.scoring import score_opportunity


def make_opportunity(**overrides):
    data = {
        "source": "github",
        "source_id": "123",
        "title": "demo/agent-kit",
        "url": "https://github.com/demo/agent-kit",
        "description": "Deployable agent workflow dashboard",
        "project": "demo/agent-kit",
        "language": "Python",
        "topics": ["ai", "agent", "workflow"],
        "stars": 1200,
        "forks": 90,
        "open_issues": 12,
        "pushed_at": datetime(2026, 5, 10, tzinfo=UTC),
        "archived": False,
        "license_spdx_id": "mit",
        "packaging_signals": ["deploy", "dashboard"],
    }
    data.update(overrides)
    return Opportunity(**data)


def make_config():
    return ScoringConfig(
        weights={
            "keyword_match": 18,
            "repo_popularity": 16,
            "recent_activity": 14,
            "packaging_fit": 22,
            "license_fit": 15,
            "low_friction": 10,
            "feedback_bonus": 5,
        },
        penalties={
            "archived_repo": -40,
            "stale_repo": -25,
            "restrictive_license": -30,
            "unknown_license": -10,
            "weak_description": -8,
        },
        preferred_licenses={"mit", "apache-2.0"},
        caution_licenses={"agpl-3.0", "gpl-3.0"},
        packaging_keywords=["deploy", "dashboard"],
    )


def test_score_rewards_active_packagable_repo():
    score = score_opportunity(
        make_opportunity(),
        make_config(),
        now=datetime(2026, 5, 15, tzinfo=UTC),
        feedback_status="new",
    )

    assert score.total >= 70
    assert "preferred license: mit" in score.reasons
    assert "packaging signals: deploy, dashboard" in score.reasons


def test_score_penalizes_archived_and_unknown_license():
    score = score_opportunity(
        make_opportunity(archived=True, license_spdx_id=None, packaging_signals=[]),
        make_config(),
        now=datetime(2026, 5, 15, tzinfo=UTC),
        feedback_status="new",
    )

    assert score.total < 40
    assert "archived repository" in score.penalties
    assert "unknown license" in score.penalties
```

- [ ] **Step 2: Run scoring tests to verify they fail**

Run:

```powershell
uv run pytest tests/test_scoring.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.scoring'
```

- [ ] **Step 3: Implement scoring engine**

```python
# src/open_source_scanner/scoring.py
from __future__ import annotations

from datetime import UTC, datetime

from open_source_scanner.models import FeedbackStatus, Opportunity, ScoreBreakdown, ScoringConfig


def score_opportunity(
    opportunity: Opportunity,
    config: ScoringConfig,
    now: datetime | None = None,
    feedback_status: FeedbackStatus = "new",
) -> ScoreBreakdown:
    now = now or datetime.now(tz=UTC)
    total = 0
    reasons: list[str] = []
    penalties: list[str] = []

    searchable = " ".join(
        [opportunity.title, opportunity.description, " ".join(opportunity.topics)]
    ).lower()
    matched_keywords = [
        keyword for keyword in config.packaging_keywords if keyword.lower() in searchable
    ]
    if matched_keywords:
        total += config.weights.get("keyword_match", 0)
        reasons.append(f"keyword match: {', '.join(matched_keywords[:5])}")

    if opportunity.stars >= 1000:
        total += config.weights.get("repo_popularity", 0)
        reasons.append("popular repository: >=1000 stars")
    elif opportunity.stars >= 100:
        total += round(config.weights.get("repo_popularity", 0) * 0.6)
        reasons.append("emerging repository: >=100 stars")

    activity_days = max((now - opportunity.pushed_at).days, 0)
    if activity_days <= 30:
        total += config.weights.get("recent_activity", 0)
        reasons.append("recent activity: <=30 days")
    elif activity_days > 180:
        total += config.penalties.get("stale_repo", 0)
        penalties.append("stale repository")

    if opportunity.packaging_signals:
        total += config.weights.get("packaging_fit", 0)
        reasons.append(f"packaging signals: {', '.join(opportunity.packaging_signals)}")

    license_id = opportunity.license_spdx_id
    if license_id in config.preferred_licenses:
        total += config.weights.get("license_fit", 0)
        reasons.append(f"preferred license: {license_id}")
    elif license_id in config.caution_licenses:
        total += config.penalties.get("restrictive_license", 0)
        penalties.append(f"caution license: {license_id}")
    elif license_id is None:
        total += config.penalties.get("unknown_license", 0)
        penalties.append("unknown license")

    if not opportunity.archived and opportunity.open_issues <= 50:
        total += config.weights.get("low_friction", 0)
        reasons.append("low operational friction")

    if feedback_status in {"saved", "watch", "package"}:
        total += config.weights.get("feedback_bonus", 0)
        reasons.append(f"user feedback: {feedback_status}")

    if opportunity.archived:
        total += config.penalties.get("archived_repo", 0)
        penalties.append("archived repository")

    if len(opportunity.description.strip()) < 20:
        total += config.penalties.get("weak_description", 0)
        penalties.append("weak description")

    return ScoreBreakdown(total=max(total, 0), reasons=reasons, penalties=penalties)
```

- [ ] **Step 4: Run scoring tests to verify they pass**

Run:

```powershell
uv run pytest tests/test_scoring.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit scoring engine**

```powershell
git add src/open_source_scanner/scoring.py tests/test_scoring.py
git commit -m "feat: score packaging opportunities"
```

---

## Task 6: Add SQLite Storage and Feedback

**Files:**
- Create: `src/open_source_scanner/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write failing storage tests**

```python
# tests/test_storage.py
from datetime import UTC, datetime

from open_source_scanner.models import Opportunity, ScoreBreakdown
from open_source_scanner.storage import OpportunityStore


def make_opportunity():
    return Opportunity(
        source="github",
        source_id="123",
        title="demo/agent-kit",
        url="https://github.com/demo/agent-kit",
        description="Deployable agent workflow dashboard",
        project="demo/agent-kit",
        language="Python",
        topics=["ai", "agent"],
        stars=1200,
        forks=90,
        open_issues=12,
        pushed_at=datetime(2026, 5, 10, tzinfo=UTC),
        archived=False,
        license_spdx_id="mit",
        packaging_signals=["deploy", "dashboard"],
    )


def test_store_upserts_opportunity_and_feedback(tmp_path):
    store = OpportunityStore(tmp_path / "scanner.sqlite")
    store.initialize()
    store.upsert_opportunity(
        make_opportunity(),
        ScoreBreakdown(total=88, reasons=["good"], penalties=[]),
        seen_at=datetime(2026, 5, 15, tzinfo=UTC),
    )
    store.set_feedback("github", "123", "package")

    rows = store.list_ranked(limit=10)

    assert len(rows) == 1
    assert rows[0]["source_id"] == "123"
    assert rows[0]["score"] == 88
    assert rows[0]["feedback_status"] == "package"
```

- [ ] **Step 2: Run storage test to verify it fails**

Run:

```powershell
uv run pytest tests/test_storage.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.storage'
```

- [ ] **Step 3: Implement SQLite store**

```python
# src/open_source_scanner/storage.py
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from open_source_scanner.models import FeedbackStatus, Opportunity, ScoreBreakdown


class OpportunityStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS opportunities (
                    source TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT NOT NULL,
                    project TEXT NOT NULL,
                    language TEXT,
                    topics_json TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    forks INTEGER NOT NULL,
                    open_issues INTEGER NOT NULL,
                    pushed_at TEXT NOT NULL,
                    archived INTEGER NOT NULL,
                    license_spdx_id TEXT,
                    packaging_signals_json TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    reasons_json TEXT NOT NULL,
                    penalties_json TEXT NOT NULL,
                    feedback_status TEXT NOT NULL DEFAULT 'new',
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    PRIMARY KEY (source, source_id)
                )
                """
            )

    def upsert_opportunity(
        self,
        opportunity: Opportunity,
        score: ScoreBreakdown,
        seen_at: datetime,
    ) -> None:
        payload = {
            "source": opportunity.source,
            "source_id": opportunity.source_id,
            "title": opportunity.title,
            "url": opportunity.url,
            "description": opportunity.description,
            "project": opportunity.project,
            "language": opportunity.language,
            "topics_json": json.dumps(opportunity.topics, ensure_ascii=False),
            "stars": opportunity.stars,
            "forks": opportunity.forks,
            "open_issues": opportunity.open_issues,
            "pushed_at": opportunity.pushed_at.isoformat(),
            "archived": int(opportunity.archived),
            "license_spdx_id": opportunity.license_spdx_id,
            "packaging_signals_json": json.dumps(opportunity.packaging_signals, ensure_ascii=False),
            "score": score.total,
            "reasons_json": json.dumps(score.reasons, ensure_ascii=False),
            "penalties_json": json.dumps(score.penalties, ensure_ascii=False),
            "seen_at": seen_at.isoformat(),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO opportunities (
                    source, source_id, title, url, description, project, language,
                    topics_json, stars, forks, open_issues, pushed_at, archived,
                    license_spdx_id, packaging_signals_json, score, reasons_json,
                    penalties_json, first_seen_at, last_seen_at
                )
                VALUES (
                    :source, :source_id, :title, :url, :description, :project, :language,
                    :topics_json, :stars, :forks, :open_issues, :pushed_at, :archived,
                    :license_spdx_id, :packaging_signals_json, :score, :reasons_json,
                    :penalties_json, :seen_at, :seen_at
                )
                ON CONFLICT(source, source_id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    description = excluded.description,
                    project = excluded.project,
                    language = excluded.language,
                    topics_json = excluded.topics_json,
                    stars = excluded.stars,
                    forks = excluded.forks,
                    open_issues = excluded.open_issues,
                    pushed_at = excluded.pushed_at,
                    archived = excluded.archived,
                    license_spdx_id = excluded.license_spdx_id,
                    packaging_signals_json = excluded.packaging_signals_json,
                    score = excluded.score,
                    reasons_json = excluded.reasons_json,
                    penalties_json = excluded.penalties_json,
                    last_seen_at = excluded.last_seen_at
                """,
                payload,
            )

    def set_feedback(self, source: str, source_id: str, status: FeedbackStatus) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE opportunities
                SET feedback_status = ?
                WHERE source = ? AND source_id = ?
                """,
                (status, source, source_id),
            )

    def list_ranked(self, limit: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM opportunities
                WHERE feedback_status != 'dismissed'
                ORDER BY score DESC, stars DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn
```

- [ ] **Step 4: Run storage test to verify it passes**

Run:

```powershell
uv run pytest tests/test_storage.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit storage**

```powershell
git add src/open_source_scanner/storage.py tests/test_storage.py
git commit -m "feat: persist opportunity history and feedback"
```

---

## Task 7: Generate Markdown Reports

**Files:**
- Create: `src/open_source_scanner/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write failing report test**

```python
# tests/test_report.py
from open_source_scanner.report import render_markdown_report


def test_render_markdown_report_lists_ranked_opportunities():
    rows = [
        {
            "title": "demo/agent-kit",
            "url": "https://github.com/demo/agent-kit",
            "project": "demo/agent-kit",
            "description": "Deployable agent workflow dashboard",
            "score": 88,
            "stars": 1200,
            "license_spdx_id": "mit",
            "packaging_signals_json": '["deploy", "dashboard"]',
            "reasons_json": '["preferred license: mit"]',
            "penalties_json": "[]",
            "feedback_status": "new",
        }
    ]

    markdown = render_markdown_report(rows, report_date="2026-05-15")

    assert "# Open Source Opportunity Report - 2026-05-15" in markdown
    assert "demo/agent-kit" in markdown
    assert "Score: 88" in markdown
    assert "Packaging signals: deploy, dashboard" in markdown
```

- [ ] **Step 2: Run report test to verify it fails**

Run:

```powershell
uv run pytest tests/test_report.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'open_source_scanner.report'
```

- [ ] **Step 3: Implement report renderer**

```python
# src/open_source_scanner/report.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_markdown_report(rows: list[dict[str, Any]], report_date: str) -> str:
    lines = [
        f"# Open Source Opportunity Report - {report_date}",
        "",
        "This report ranks open-source projects by packaging and monetization potential.",
        "",
    ]
    if not rows:
        lines.extend(["No opportunities found for this run.", ""])
        return "\n".join(lines)

    for index, row in enumerate(rows, start=1):
        signals = json.loads(row["packaging_signals_json"])
        reasons = json.loads(row["reasons_json"])
        penalties = json.loads(row["penalties_json"])
        lines.extend(
            [
                f"## {index}. {row['title']}",
                "",
                f"- URL: {row['url']}",
                f"- Score: {row['score']}",
                f"- Stars: {row['stars']}",
                f"- License: {row['license_spdx_id'] or 'unknown'}",
                f"- Feedback: {row['feedback_status']}",
                f"- Packaging signals: {', '.join(signals) if signals else 'none'}",
                f"- Description: {row['description']}",
                f"- Reasons: {', '.join(reasons) if reasons else 'none'}",
                f"- Penalties: {', '.join(penalties) if penalties else 'none'}",
                "",
            ]
        )
    return "\n".join(lines)


def write_report(rows: list[dict[str, Any]], report_date: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{report_date}.md"
    output_path.write_text(render_markdown_report(rows, report_date), encoding="utf-8")
    return output_path
```

- [ ] **Step 4: Run report test to verify it passes**

Run:

```powershell
uv run pytest tests/test_report.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit report generation**

```powershell
git add src/open_source_scanner/report.py tests/test_report.py
git commit -m "feat: generate markdown opportunity reports"
```

---

## Task 8: Wire CLI Commands

**Files:**
- Create: `src/open_source_scanner/__main__.py`
- Modify: `README.md`

- [ ] **Step 1: Implement CLI**

```python
# src/open_source_scanner/__main__.py
from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import typer
from rich.console import Console

from open_source_scanner.config import load_scanner_config
from open_source_scanner.connectors.github import GitHubConnector
from open_source_scanner.normalize import normalize_repository
from open_source_scanner.report import write_report
from open_source_scanner.scoring import score_opportunity
from open_source_scanner.storage import OpportunityStore


app = typer.Typer(help="Scan open-source projects for packaging opportunities.")
console = Console()


def _store() -> OpportunityStore:
    db_path = Path(os.getenv("OSS_SCANNER_DB", "data/scanner.sqlite"))
    store = OpportunityStore(db_path)
    store.initialize()
    return store


@app.command()
def scan(
    config_dir: Path = typer.Option(Path("config"), help="Directory containing sources.yml and scoring.yml."),
    limit: int = typer.Option(50, help="Maximum repositories per query."),
) -> None:
    config = load_scanner_config(config_dir)
    store = _store()
    now = datetime.now(tz=UTC)

    if not config.github.enabled:
        console.print("[yellow]GitHub source is disabled.[/yellow]")
        raise typer.Exit()

    connector = GitHubConnector()
    written = 0
    try:
        for query in config.github.repository_queries:
            repos = connector.search_repositories(query, limit=min(limit, config.github.max_results))
            for repo in repos:
                opportunity = normalize_repository(repo, config.scoring.packaging_keywords)
                score = score_opportunity(opportunity, config.scoring, now=now)
                store.upsert_opportunity(opportunity, score, seen_at=now)
                written += 1
    finally:
        connector.close()

    console.print(f"[green]Scanned and stored {written} opportunity observations.[/green]")


@app.command()
def report(
    today: bool = typer.Option(False, help="Use today's date for the report filename."),
    limit: int = typer.Option(20, help="Number of ranked opportunities to include."),
    output_dir: Path = typer.Option(Path("reports"), help="Report output directory."),
) -> None:
    report_date = datetime.now(tz=UTC).date().isoformat() if today else datetime.now(tz=UTC).date().isoformat()
    store = _store()
    rows = store.list_ranked(limit=limit)
    path = write_report(rows, report_date=report_date, output_dir=output_dir)
    console.print(f"[green]Report written to {path}[/green]")


@app.command()
def feedback(
    source: str = typer.Argument(..., help="Opportunity source, such as github."),
    source_id: str = typer.Argument(..., help="Source-specific opportunity id."),
    status: str = typer.Argument(..., help="new, saved, dismissed, watch, or package."),
) -> None:
    allowed = {"new", "saved", "dismissed", "watch", "package"}
    if status not in allowed:
        console.print(f"[red]Invalid status. Use one of: {', '.join(sorted(allowed))}[/red]")
        raise typer.Exit(code=1)
    store = _store()
    store.set_feedback(source, source_id, status)  # type: ignore[arg-type]
    console.print(f"[green]Feedback saved for {source}:{source_id} -> {status}[/green]")


if __name__ == "__main__":
    app()
```

- [ ] **Step 2: Run CLI help**

Run:

```powershell
uv run oss-scan --help
```

Expected:

```text
Usage:
```

- [ ] **Step 3: Run tests**

Run:

```powershell
uv run pytest -v
```

Expected:

```text
6 passed
```

- [ ] **Step 4: Run linter**

Run:

```powershell
uv run ruff check .
```

Expected:

```text
All checks passed!
```

- [ ] **Step 5: Update `README.md` usage section**

Add this section:

```markdown
## Commands

```powershell
uv run oss-scan scan --limit 50
uv run oss-scan report --today
uv run oss-scan feedback github 123 package
```

Feedback statuses:

- `new`: default state
- `saved`: interesting but not urgent
- `dismissed`: hide from ranked reports
- `watch`: keep tracking
- `package`: create a deeper packaging memo
```

- [ ] **Step 6: Commit CLI**

```powershell
git add src/open_source_scanner/__main__.py README.md
git commit -m "feat: wire scanner cli"
```

---

## Task 9: Document the Packaging Workflow

**Files:**
- Create: `docs/opportunity-workflow.md`

- [ ] **Step 1: Create workflow document**

```markdown
# Opportunity Workflow

## Purpose

This workflow turns public open-source signals into a short list of projects worth evaluating for legal and ethical packaging.

## Funnel

1. Discovery: collect public project metadata from GitHub.
2. Scoring: rank projects by pain, packaging fit, activity, license fit, and friction.
3. Review: mark each project as `saved`, `dismissed`, `watch`, or `package`.
4. Memo: for `package` items, write a one-page opportunity memo.
5. Experiment: validate interest with a landing page, demo, template, hosted prototype, or direct outreach.

## Packaging Paths

- Hosted SaaS: provide an easier hosted version of a self-hosted tool.
- Deployment kit: provide scripts, Docker Compose, Terraform, or one-click deploys.
- Vertical template: adapt a generic tool for a specific niche.
- Localization: provide Chinese documentation, examples, and support.
- Integration: connect a tool to Notion, Slack, GitHub, WeChat, Feishu, or common data systems.
- Training and support: sell implementation help, guides, or maintenance.

## Evaluation Questions

- Who has the problem?
- What is hard about using the original project directly?
- What would a paid wrapper make easier?
- Does the license allow the intended packaging path?
- Is the original project active enough to build around?
- Can a useful demo be produced in seven days?

## Stop Conditions

- The license creates unacceptable commercial risk.
- The project is inactive and difficult to maintain.
- The target user is unclear.
- The packaging idea does not add meaningful value beyond rebranding.
- There are strong competitors with better distribution and no clear niche.
```

- [ ] **Step 2: Commit workflow document**

```powershell
git add docs/opportunity-workflow.md
git commit -m "docs: define opportunity workflow"
```

---

## Task 10: Add Optional Scheduled Automation

**Files:**
- Create: `.github/workflows/daily-scan.yml`
- Modify: `README.md`

- [ ] **Step 1: Create GitHub Actions workflow**

```yaml
name: Daily opportunity scan

on:
  schedule:
    - cron: "0 1 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync

      - name: Run scan
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          uv run oss-scan scan --limit 50
          uv run oss-scan report --today

      - name: Commit report
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add reports data/.gitkeep
          git diff --cached --quiet || git commit -m "chore: update daily opportunity report"
          git push
```

- [ ] **Step 2: Add local Windows scheduling instructions to `README.md`**

Add:

```markdown
## Local scheduled run on Windows

Create a PowerShell script such as `scripts/run-daily-scan.ps1`:

```powershell
Set-Location "E:\AI\resp_scanner"
uv run oss-scan scan --limit 50
uv run oss-scan report --today
```

Then schedule that script with Windows Task Scheduler to run daily.
```

- [ ] **Step 3: Commit automation documentation**

```powershell
git add .github/workflows/daily-scan.yml README.md
git commit -m "chore: add optional scheduled scan workflow"
```

---

## Task 11: End-to-End Verification

**Files:**
- Modify only if a verification failure reveals an issue in previous tasks.

- [ ] **Step 1: Run all tests**

```powershell
uv run pytest -v
```

Expected:

```text
6 passed
```

- [ ] **Step 2: Run lint**

```powershell
uv run ruff check .
```

Expected:

```text
All checks passed!
```

- [ ] **Step 3: Run a real scan**

Run with a token in the shell:

```powershell
$env:GITHUB_TOKEN="your_token"
uv run oss-scan scan --limit 5
```

Expected:

```text
Scanned and stored ... opportunity observations.
```

- [ ] **Step 4: Generate report**

```powershell
uv run oss-scan report --today --limit 10
```

Expected:

```text
Report written to reports/YYYY-MM-DD.md
```

- [ ] **Step 5: Inspect report quality**

Open the generated report and confirm each ranked item has:

- Project name
- URL
- Score
- Stars
- License
- Packaging signals
- Reasons
- Penalties

- [ ] **Step 6: Verify secret hygiene**

Run:

```powershell
git status --short
git diff -- .env data reports
```

Expected:

```text
No .env file is staged.
No token value appears in tracked diffs.
```

---

## Risks and Caveats

- GitHub search rate limits can interrupt unauthenticated scans. Use `GITHUB_TOKEN` for regular runs.
- Star count is only a rough popularity signal. The scoring system must be tuned with user feedback.
- License checks are only initial filters. A project marked as commercially interesting still needs manual license review before productization.
- A high score means "worth evaluating", not "safe to commercialize immediately".
- GitHub Actions commits generated reports to the repository. Use local scheduling instead if reports should remain private.

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md`. Two execution options:

1. Subagent-Driven (recommended): dispatch a fresh subagent per task, review between tasks, and keep each change small.
2. Inline Execution: execute tasks in this session with checkpoints after each batch.

Recommended next choice: start with Inline Execution for Tasks 1-4 because the repository is still small, then switch to Subagent-Driven when adding more data sources.
