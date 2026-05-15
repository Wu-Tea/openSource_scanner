from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STATUS_ORDER = ("package", "watch", "saved", "new", "dismissed")

NEXT_ACTIONS = {
    "package": "Next action: create or review memo, then design a 7-day experiment.",
    "watch": "Next action: keep monitoring activity and pain signals.",
    "saved": "Next action: decide whether to watch or package.",
    "new": "Next action: decide whether this belongs in saved, watch, or package.",
    "dismissed": "Next action: no action unless new evidence changes the decision.",
}


def render_shortlist(rows: list[dict[str, Any]], report_date: str) -> str:
    lines = [
        f"# Open Source Opportunity Shortlist - {report_date}",
        "",
        "This lightweight pipeline groups opportunities by feedback status.",
        "",
    ]

    if not rows:
        lines.extend(
            [
                "No shortlisted opportunities yet.",
                "",
                "Use feedback statuses like `saved`, `watch`, or `package` to turn report "
                "decisions into this tracking view.",
                "",
            ]
        )
        return "\n".join(lines)

    grouped = _group_by_status(rows)
    for status in STATUS_ORDER:
        status_rows = grouped.get(status, [])
        if not status_rows:
            continue
        lines.extend([f"## {status.title()}", ""])
        for index, row in enumerate(status_rows, start=1):
            lines.extend(_render_item(index, row, status))

    return "\n".join(lines)


def write_shortlist(rows: list[dict[str, Any]], report_date: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_shortlist(rows, report_date), encoding="utf-8")
    return output_path


def _group_by_status(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        status = str(row.get("feedback_status") or "new")
        grouped.setdefault(status, []).append(row)
    return grouped


def _render_item(index: int, row: dict[str, Any], status: str) -> list[str]:
    title = str(row.get("title") or row.get("project") or row.get("source_id") or "unknown")
    source = str(row.get("source") or "unknown")
    source_id = str(row.get("source_id") or "unknown")
    packaging_signals = _decode_json_list(row.get("packaging_signals_json"))

    return [
        f"### {index}. {title}",
        "",
        f"- URL: {row.get('url') or 'unknown'}",
        f"- Feedback target: {source} {source_id}",
        f"- Score: {row.get('score', 'unknown')}",
        f"- Stars: {row.get('stars', 'unknown')}",
        f"- License: {row.get('license_spdx_id') or 'unknown'}",
        f"- Packaging signals: {_format_list(packaging_signals)}",
        f"- {NEXT_ACTIONS.get(status, NEXT_ACTIONS['new'])}",
        "",
    ]


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


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"
