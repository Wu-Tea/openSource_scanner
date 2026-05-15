from __future__ import annotations

from open_source_scanner.taxonomy import balance_rows_by_category, classify_row


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
