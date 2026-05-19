from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any


OTHER_CATEGORY = "Other"
VERTICAL_OTHER_CATEGORY = "Other"

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

VERTICAL_DEFINITIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Restaurant / Hospitality",
        (
            "restaurant",
            "hospitality",
            "hotel",
            "menu",
            "table reservation",
            "online ordering",
            "salon",
            "barber",
            "takeaway",
            "delivery",
            "room booking",
            "booking platform",
        ),
    ),
    (
        "Booking / Scheduling",
        (
            "booking",
            "appointment",
            "reservation",
            "scheduling",
            "calendar",
            "staff scheduling",
            "employee scheduling",
            "roster",
        ),
    ),
    (
        "Forms / Surveys / Documents",
        (
            "form",
            "survey",
            "questionnaire",
            "document management",
            "pdf",
            "resume",
            "contract",
            "receipt",
            "spreadsheet",
            "invoice",
        ),
    ),
    (
        "CRM / Sales / Support",
        (
            "crm",
            "customer lifecycle",
            "helpdesk",
            "ticketing",
            "shared inbox",
            "customer support",
            "service desk",
            "help center",
            "customer portal",
            "sales",
        ),
    ),
    (
        "Inventory / Assets / Field Ops",
        (
            "inventory",
            "asset management",
            "warehouse",
            "pantry",
            "barcode",
            "stock",
            "field service",
            "maintenance",
            "work order",
            "equipment",
        ),
    ),
    (
        "Real Estate / Property",
        (
            "real estate",
            "property",
            "rental",
            "landlord",
            "tenant",
            "lease",
            "apartment",
            "room",
        ),
    ),
    (
        "Healthcare / Clinic",
        (
            "clinic",
            "hospital",
            "dental",
            "veterinary",
            "patient",
            "medical",
            "healthcare",
            "blood bank",
            "practice management",
        ),
    ),
    (
        "Education / Training",
        (
            "school",
            "daycare",
            "student",
            "teacher",
            "learning management",
            "lms",
            "course",
            "classroom",
            "training",
        ),
    ),
    (
        "Finance / Billing",
        (
            "billing",
            "payment",
            "pricing",
            "subscription",
            "bookkeeping",
            "personal finance",
            "expense",
            "budget",
            "splitwise",
        ),
    ),
    (
        "Events / Membership",
        (
            "event management",
            "event ticketing",
            "ticketing",
            "membership",
            "member directory",
            "club",
            "volunteer",
            "donation",
        ),
    ),
)

GENERIC_WEB_FRAMEWORK_TERMS = (
    "web framework",
    "frontend",
    "backend",
    "react",
    "vue",
    "svelte",
    "nextjs",
    "tailwind",
    "laravel",
    "django",
    "rails",
    "nestjs",
    "symfony",
    "component",
    "components",
    "starter",
    "boilerplate",
    "template",
    "theme",
    "css",
    "ui library",
    "module",
    "modules",
)

GENERIC_TECH_TERMS = (
    "framework",
    "library",
    "sdk",
    "api",
    "infrastructure",
    "developer tools",
    "kubernetes",
    "terraform",
    "devops",
    "llm",
    "agent",
    "mcp",
)

VERTICAL_FALSE_POSITIVE_TERMS = (
    "developer",
    "developers",
    "developer tools",
    "framework",
    "library",
    "helper library",
    "code examples",
    "examples",
    "awesome",
    "awesome list",
    "knowledge list",
    "cloud platforms",
    "python wrapper",
    "wrapper",
    "modules",
    "utilities",
    "sdk",
    "api developers",
    "event driven",
    "event studies",
    "event stream",
    "microservices",
    "laravel",
    "django",
    "rails",
    "nestjs",
    "symfony",
    "kubernetes",
    "terraform",
    "ansible",
    "netbox",
    "dcim",
    "ipam",
    "configuration management",
    "infrastructure management",
    "cloud management",
    "remote execution",
    "devops",
    "aws security",
    "offensive",
    "pentest",
    "llm",
    "agent",
    "mcp",
    "obsidian",
    "personal",
    "tutorial",
    "tutorials",
    "papers",
    "research",
    "causal inference",
    "sklearn",
    "paper",
    "arxiv",
    "api testing",
    "property based testing",
    "pytest",
    "fuzzing",
    "graphql",
    "openapi",
    "swagger",
    "godot",
    "game development",
    "editor plugin",
    "mapbox",
    "maplibre",
    "scraping",
    "scraper",
    "python package",
)

BUSINESS_CONTEXT_TERMS = (
    "small business",
    "business",
    "enterprise",
    "restaurant",
    "hospitality",
    "hotel",
    "salon",
    "barber",
    "clinic",
    "hospital",
    "doctor",
    "patient",
    "dental",
    "veterinary",
    "school",
    "student",
    "teacher",
    "daycare",
    "invoice",
    "quote",
    "billing",
    "payment",
    "bookkeeping",
    "expense",
    "form builder",
    "survey",
    "questionnaire",
    "document management",
    "contract",
    "receipt",
    "crm",
    "customer",
    "helpdesk",
    "service desk",
    "customer portal",
    "inventory",
    "warehouse",
    "barcode",
    "stock",
    "pos",
    "repair shop",
    "field service",
    "maintenance",
    "work order",
    "equipment rental",
    "property",
    "real estate",
    "tenant",
    "landlord",
    "lease",
    "apartment",
    "booking",
    "appointment",
    "reservation",
    "staff scheduling",
    "event management",
    "event ticketing",
    "membership",
    "volunteer",
    "nonprofit",
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


def classify_vertical_row(row: dict[str, Any]) -> str:
    text = _row_text(row)
    tokens = text.split()
    scores: Counter[str] = Counter()
    for category, keywords in VERTICAL_DEFINITIONS:
        for keyword in keywords:
            keyword_score = _keyword_score(keyword, text, tokens)
            if keyword_score:
                scores[category] += keyword_score

    if not scores:
        return VERTICAL_OTHER_CATEGORY
    return max(scores, key=lambda category: scores[category])


def rank_rows_for_vertical_report(
    rows: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    ranked = sorted(
        (_with_vertical_category(row) for row in rows),
        key=_vertical_sort_key,
        reverse=True,
    )
    return ranked[:limit]


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


def _with_vertical_category(row: dict[str, Any]) -> dict[str, Any]:
    vertical_category = classify_vertical_row(row)
    category = (
        f"Vertical: {vertical_category}"
        if vertical_category != VERTICAL_OTHER_CATEGORY
        else classify_row(row)
    )
    return {
        **row,
        "category": category,
        "vertical_category": vertical_category,
        "vertical_score": _vertical_score(row, vertical_category),
    }


def _vertical_score(row: dict[str, Any], vertical_category: str) -> int:
    score = int(row.get("score") or 0)
    category = classify_row(row)
    text = _row_text(row)
    tokens = text.split()
    business_context_hits = _business_context_count(text, tokens)

    if vertical_category != VERTICAL_OTHER_CATEGORY:
        score += 25
        score += min(_matched_vertical_keyword_count(text, tokens) * 4, 24)
        if business_context_hits:
            score += min(business_context_hits * 8, 40)
        else:
            score -= 45
    else:
        score -= 20

    if category == "Web / App Frameworks":
        score -= 45
    elif category in {"Developer Tools", "Infra / DevOps", "AI / Agents"}:
        score -= 35
    elif category == "Productivity / Knowledge":
        score -= 35
    elif category == "Security / Privacy" and vertical_category != VERTICAL_OTHER_CATEGORY:
        score -= 20

    generic_web_hits = sum(_keyword_score(term, text, tokens) for term in GENERIC_WEB_FRAMEWORK_TERMS)
    if generic_web_hits:
        score -= min(generic_web_hits * 8, 40)

    false_positive_hits = sum(_keyword_score(term, text, tokens) for term in VERTICAL_FALSE_POSITIVE_TERMS)
    if false_positive_hits:
        score -= min(false_positive_hits * 16, 112)
        if not business_context_hits:
            score -= 35

    if vertical_category == VERTICAL_OTHER_CATEGORY:
        generic_tech_hits = sum(_keyword_score(term, text, tokens) for term in GENERIC_TECH_TERMS)
        score -= min(generic_tech_hits * 5, 30)

    return score


def _vertical_sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        int(row.get("vertical_score") or 0),
        int(row.get("score") or 0),
        int(row.get("stars") or 0),
        str(row.get("title") or ""),
    )


def _matched_vertical_keyword_count(text: str, tokens: list[str]) -> int:
    count = 0
    for _, keywords in VERTICAL_DEFINITIONS:
        for keyword in keywords:
            if _keyword_score(keyword, text, tokens):
                count += 1
    return count


def _business_context_count(text: str, tokens: list[str]) -> int:
    return sum(_keyword_score(term, text, tokens) for term in BUSINESS_CONTEXT_TERMS)


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


def _row_text(row: dict[str, Any]) -> str:
    return _normalized_text(
        [
            row.get("title"),
            row.get("project"),
            row.get("description"),
            row.get("language"),
            *_decode_json_list(row.get("topics_json")),
            *_decode_json_list(row.get("packaging_signals_json")),
        ]
    )


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
