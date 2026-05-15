from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any


OTHER_CATEGORY = "Other"

CATEGORY_DEFINITIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Security / Privacy",
        (
            "security",
            "privacy",
            "auth",
            "oauth",
            "sso",
            "iam",
            "vulnerability",
            "scanner",
            "firewall",
            "zero trust",
            "compliance",
        ),
    ),
    (
        "Infra / DevOps",
        (
            "self hosted",
            "selfhosted",
            "devops",
            "ops",
            "docker",
            "kubernetes",
            "k8s",
            "deploy",
            "deployment",
            "observability",
            "monitoring",
            "logs",
            "terraform",
            "homelab",
            "proxy",
            "gateway",
        ),
    ),
    (
        "Data / Analytics",
        (
            "data",
            "analytics",
            "etl",
            "database",
            "postgres",
            "mysql",
            "warehouse",
            "dashboard",
            "bi",
            "streaming",
            "pipeline",
            "visualization",
            "metrics",
        ),
    ),
    (
        "Developer Tools",
        (
            "developer tools",
            "devtools",
            "cli",
            "sdk",
            "api",
            "testing",
            "test",
            "linter",
            "formatter",
            "debugging",
            "ide",
            "vscode",
            "git",
            "github",
            "package manager",
        ),
    ),
    (
        "Automation / Workflow",
        (
            "automation",
            "workflow",
            "rpa",
            "no code",
            "nocode",
            "low code",
            "integration",
            "integrations",
            "scheduler",
            "orchestration",
        ),
    ),
    (
        "AI / Agents",
        (
            "ai",
            "llm",
            "agent",
            "agents",
            "rag",
            "mcp",
            "openai",
            "claude",
            "machine learning",
            "ml",
            "generative ai",
            "embedding",
            "vector",
            "copilot",
        ),
    ),
    (
        "Productivity / Knowledge",
        (
            "productivity",
            "knowledge",
            "notes",
            "notion",
            "wiki",
            "docs",
            "document",
            "bookmark",
            "calendar",
            "email",
            "personal",
        ),
    ),
    (
        "Commerce / Growth",
        (
            "commerce",
            "ecommerce",
            "shopify",
            "stripe",
            "billing",
            "payment",
            "crm",
            "marketing",
            "sales",
            "seo",
        ),
    ),
    (
        "Media / Design",
        (
            "media",
            "image",
            "video",
            "audio",
            "design",
            "figma",
            "editor",
            "camera",
            "photography",
        ),
    ),
    (
        "Web / App Frameworks",
        (
            "web",
            "framework",
            "frontend",
            "backend",
            "react",
            "vue",
            "svelte",
            "nextjs",
            "serverless",
            "cms",
            "blog",
        ),
    ),
)


def classify_row(row: dict[str, Any]) -> str:
    explicit_category = row.get("category")
    if explicit_category:
        return str(explicit_category)

    text = _normalized_text(
        [
            row.get("title"),
            row.get("project"),
            row.get("description"),
            row.get("language"),
            *_decode_json_list(row.get("topics_json")),
        ]
    )
    tokens = text.split()
    scores: Counter[str] = Counter()
    for category, keywords in CATEGORY_DEFINITIONS:
        for keyword in keywords:
            keyword_score = _keyword_score(keyword, text, tokens)
            if keyword_score:
                scores[category] += keyword_score

    if not scores:
        return OTHER_CATEGORY
    return max(scores, key=lambda category: scores[category])


def balance_rows_by_category(
    rows: list[dict[str, Any]],
    *,
    limit: int,
    per_category: int,
) -> list[dict[str, Any]]:
    if limit <= 0:
        return []

    category_cap = max(per_category, 1)
    categorized_rows = [_with_category(row) for row in rows]
    selected: list[dict[str, Any]] = []
    selected_keys: set[tuple[str, str, str, str]] = set()
    category_counts: Counter[str] = Counter()

    for row in categorized_rows:
        category = str(row["category"])
        if category_counts[category] >= category_cap:
            continue
        selected.append(row)
        selected_keys.add(_row_key(row))
        category_counts[category] += 1
        if len(selected) >= limit:
            return selected

    for row in categorized_rows:
        if _row_key(row) in selected_keys:
            continue
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def _with_category(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("category"):
        return dict(row)
    return {**row, "category": classify_row(row)}


def _row_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("source", "")),
        str(row.get("source_id", "")),
        str(row.get("title", "")),
        str(row.get("url", "")),
    )


def _decode_json_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        decoded = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(decoded, list):
        return []
    return [str(item) for item in decoded]


def _normalized_text(values: list[Any]) -> str:
    joined = " ".join(str(value) for value in values if value is not None)
    return re.sub(r"[^a-z0-9]+", " ", joined.casefold()).strip()


def _keyword_score(keyword: str, text: str, tokens: list[str]) -> int:
    normalized_keyword = _normalized_text([keyword])
    if not normalized_keyword:
        return 0
    if " " in normalized_keyword:
        return text.count(normalized_keyword)
    return tokens.count(normalized_keyword)
