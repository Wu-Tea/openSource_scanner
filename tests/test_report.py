from __future__ import annotations

from pathlib import Path

from open_source_scanner.report import render_markdown_report, write_report


def test_render_markdown_report_lists_ranked_opportunities():
    rows = [
        {
            "title": "demo/agent-kit",
            "url": "https://github.com/demo/agent-kit",
            "description": "Deployable agent workflow dashboard",
            "score": 88,
            "stars": 1200,
            "license_spdx_id": "mit",
            "packaging_signals_json": '["deploy", "dashboard"]',
            "reasons_json": '["preferred license: mit"]',
            "penalties_json": '["open issues are elevated"]',
            "feedback_status": "new",
        }
    ]

    markdown = render_markdown_report(rows, report_date="2026-05-15")

    assert "# Open Source Opportunity Report - 2026-05-15" in markdown
    assert "This report ranks open-source projects" in markdown
    assert "demo/agent-kit" in markdown
    assert "Score: 88" in markdown
    assert "Packaging signals: deploy, dashboard" in markdown
    assert "Reasons: preferred license: mit" in markdown
    assert "Penalties: open issues are elevated" in markdown


def test_render_markdown_report_handles_empty_rows():
    markdown = render_markdown_report([], report_date="2026-05-15")

    assert "# Open Source Opportunity Report - 2026-05-15" in markdown
    assert "No opportunities found" in markdown


def test_render_markdown_report_handles_malformed_json_fields():
    rows = [
        {
            "title": "demo/bad-json",
            "url": "https://github.com/demo/bad-json",
            "description": "Report row with malformed JSON fields",
            "score": 42,
            "stars": 10,
            "license_spdx_id": None,
            "packaging_signals_json": "not-json",
            "reasons_json": "not-json",
            "penalties_json": "not-json",
            "feedback_status": "new",
        }
    ]

    markdown = render_markdown_report(rows, report_date="2026-05-15")

    assert "Packaging signals: none" in markdown
    assert "Reasons: none" in markdown
    assert "Penalties: none" in markdown


def test_write_report_creates_output_directory_and_dated_file(tmp_path: Path):
    output_path = write_report([], report_date="2026-05-15", output_dir=tmp_path / "reports")

    assert output_path == tmp_path / "reports" / "2026-05-15.md"
    assert output_path.read_text(encoding="utf-8").startswith(
        "# Open Source Opportunity Report - 2026-05-15"
    )
