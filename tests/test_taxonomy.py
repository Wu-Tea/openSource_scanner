from __future__ import annotations

from open_source_scanner.taxonomy import (
    balance_rows_by_category,
    classify_row,
    classify_vertical_row,
    rank_rows_for_vertical_report,
)


def test_classify_row_detects_ai_agent_projects() -> None:
    row = {
        "title": "demo/agent-memory",
        "description": "Memory backend for LLM agents",
        "topics_json": '["ai", "llm", "mcp"]',
        "packaging_signals_json": '["api"]',
    }

    assert classify_row(row) == "AI / Agents"


def test_classify_row_detects_infra_before_generic_api_signal() -> None:
    row = {
        "title": "demo/kube-dashboard",
        "description": "Self-hosted Kubernetes deployment dashboard",
        "topics_json": '["kubernetes", "docker", "self-hosted"]',
        "packaging_signals_json": '["api", "dashboard"]',
    }

    assert classify_row(row) == "Infra / DevOps"


def test_classify_row_falls_back_to_other() -> None:
    row = {
        "title": "demo/quiet-library",
        "description": "Small collection of helper functions",
        "topics_json": "[]",
        "packaging_signals_json": "[]",
    }

    assert classify_row(row) == "Other"


def test_balance_rows_by_category_prioritizes_category_variety() -> None:
    rows = [
        _row("ai-1", "AI / Agents", 100),
        _row("ai-2", "AI / Agents", 99),
        _row("ai-3", "AI / Agents", 98),
        _row("infra-1", "Infra / DevOps", 80),
        _row("security-1", "Security / Privacy", 70),
    ]

    balanced = balance_rows_by_category(rows, limit=4, per_category=1)

    assert [row["source_id"] for row in balanced] == [
        "ai-1",
        "infra-1",
        "security-1",
        "ai-2",
    ]


def test_classify_vertical_row_detects_specific_business_workflow() -> None:
    row = {
        "title": "demo/restaurant-booking",
        "description": "Restaurant online ordering, table reservation, menu, billing, and staff dashboard",
        "topics_json": '["restaurant-management", "booking-system"]',
        "packaging_signals_json": '["dashboard"]',
    }

    assert classify_vertical_row(row) == "Restaurant / Hospitality"


def test_vertical_report_ranking_downranks_generic_web_frameworks() -> None:
    rows = [
        {
            "source_id": "framework",
            "title": "demo/react-starter",
            "description": "React web framework starter with components and frontend templates",
            "score": 90,
            "stars": 50000,
            "topics_json": '["react", "frontend", "web-framework"]',
            "packaging_signals_json": '["template"]',
        },
        {
            "source_id": "restaurant",
            "title": "demo/restaurant-booking",
            "description": "Restaurant online ordering, table reservation, menu, billing, and staff dashboard",
            "score": 61,
            "stars": 80,
            "topics_json": '["restaurant-management", "booking-system"]',
            "packaging_signals_json": '["dashboard"]',
        },
    ]

    ranked = rank_rows_for_vertical_report(rows, limit=2)

    assert [row["source_id"] for row in ranked] == ["restaurant", "framework"]
    assert ranked[0]["category"] == "Vertical: Restaurant / Hospitality"


def test_vertical_report_downranks_frameworks_with_generic_event_terms() -> None:
    rows = [
        {
            "source_id": "nestjs",
            "title": "demo/nestjs-modules",
            "description": "A framework collection of modules and utilities for event-driven API developers",
            "score": 95,
            "stars": 20000,
            "topics_json": '["nestjs", "framework", "developer-tools"]',
            "packaging_signals_json": '["plugin"]',
        },
        {
            "source_id": "volunteer",
            "title": "demo/volunteer-manager",
            "description": "Volunteer and event management platform for local nonprofit organizations",
            "score": 55,
            "stars": 80,
            "topics_json": '["volunteer-management", "event-management"]',
            "packaging_signals_json": '["dashboard"]',
        },
    ]

    ranked = rank_rows_for_vertical_report(rows, limit=2)

    assert [row["source_id"] for row in ranked] == ["volunteer", "nestjs"]


def _row(source_id: str, category: str, score: int) -> dict[str, object]:
    return {
        "source_id": source_id,
        "title": f"demo/{source_id}",
        "description": category,
        "score": score,
        "topics_json": "[]",
        "packaging_signals_json": "[]",
        "category": category,
    }
