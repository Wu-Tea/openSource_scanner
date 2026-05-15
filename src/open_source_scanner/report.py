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
        packaging_signals = _decode_json_list(row.get("packaging_signals_json"))
        reasons = _decode_json_list(row.get("reasons_json"))
        penalties = _decode_json_list(row.get("penalties_json"))
        lines.extend(
            [
                f"## {index}. {row['title']}",
                "",
                f"- URL: {row['url']}",
                f"- Feedback target: {row.get('source', 'unknown')} {row.get('source_id', 'unknown')}",
                f"- Score: {row['score']}",
                f"- Stars: {row['stars']}",
                f"- License: {row.get('license_spdx_id') or 'unknown'}",
                f"- Feedback: {row.get('feedback_status', 'new')}",
                f"- Packaging signals: {_format_list(packaging_signals)}",
                f"- Description: {row.get('description') or 'No description provided.'}",
                f"- Reasons: {_format_list(reasons)}",
                f"- Penalties: {_format_list(penalties)}",
                "",
            ]
        )

    return "\n".join(lines)


def write_report(rows: list[dict[str, Any]], report_date: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{report_date}.md"
    output_path.write_text(render_markdown_report(rows, report_date), encoding="utf-8")
    return output_path


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
