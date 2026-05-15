from __future__ import annotations

from pathlib import Path

from open_source_scanner.shortlist import render_shortlist, write_shortlist


def test_render_shortlist_groups_rows_and_decodes_packaging_signals() -> None:
    rows = [
        {
            "source": "github",
            "source_id": "watch-1",
            "title": "demo/watch-kit",
            "url": "https://github.com/demo/watch-kit",
            "feedback_status": "watch",
            "score": 70,
            "stars": 900,
            "license_spdx_id": "apache-2.0",
            "packaging_signals_json": '["workflow", "dashboard"]',
        },
        {
            "source": "github",
            "source_id": "package-1",
            "title": "demo/package-kit",
            "url": "https://github.com/demo/package-kit",
            "feedback_status": "package",
            "score": 65,
            "stars": 300,
            "license_spdx_id": "mit",
            "packaging_signals_json": ["deploy", "hosted"],
        },
        {
            "source": "github",
            "source_id": "saved-1",
            "title": "demo/saved-kit",
            "url": "https://github.com/demo/saved-kit",
            "feedback_status": "saved",
            "score": 88,
            "stars": 1200,
            "license_spdx_id": None,
            "packaging_signals_json": "not json",
        },
    ]

    markdown = render_shortlist(rows, report_date="2026-05-15")

    assert "# Open Source Opportunity Shortlist - 2026-05-15" in markdown
    assert markdown.index("## Package") < markdown.index("## Watch") < markdown.index("## Saved")
    assert "demo/package-kit" in markdown
    assert "Feedback target: github package-1" in markdown
    assert "Packaging signals: deploy, hosted" in markdown
    assert "Packaging signals: workflow, dashboard" in markdown
    assert "Packaging signals: none" in markdown
    assert "create or review memo" in markdown
    assert "design a 7-day experiment" in markdown
    assert "keep monitoring activity and pain signals" in markdown
    assert "decide whether to watch or package" in markdown


def test_render_shortlist_empty_output_explains_feedback_statuses() -> None:
    markdown = render_shortlist([], report_date="2026-05-15")

    assert "# Open Source Opportunity Shortlist - 2026-05-15" in markdown
    assert "No shortlisted opportunities yet." in markdown
    assert "saved" in markdown
    assert "watch" in markdown
    assert "package" in markdown


def test_write_shortlist_creates_parent_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "reports" / "shortlist.md"

    written_path = write_shortlist([], report_date="2026-05-15", output_path=output_path)

    assert written_path == output_path
    assert output_path.exists()
    assert "Open Source Opportunity Shortlist" in output_path.read_text(encoding="utf-8")
