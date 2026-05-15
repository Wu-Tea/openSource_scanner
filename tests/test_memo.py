from __future__ import annotations

from pathlib import Path

from open_source_scanner.memo import render_opportunity_memo, write_opportunity_memo


def _row() -> dict[str, object]:
    return {
        "source": "github",
        "source_id": "123",
        "title": "demo/agent-kit",
        "project": "demo/agent-kit",
        "url": "https://github.com/demo/agent-kit",
        "description": "Deployable agent workflow dashboard",
        "score": 88,
        "stars": 1200,
        "license_spdx_id": "mit",
        "feedback_status": "package",
        "packaging_signals_json": '["deploy", "dashboard", "integration"]',
        "reasons_json": '["preferred license: mit", "recent activity"]',
        "penalties_json": '["open issues are elevated"]',
    }


def test_render_opportunity_memo_includes_review_sections() -> None:
    markdown = render_opportunity_memo(_row(), memo_date="2026-05-15")

    assert "# Opportunity Memo - demo/agent-kit" in markdown
    assert "Generated date: 2026-05-15" in markdown
    assert "Feedback target: github 123" in markdown
    assert "https://github.com/demo/agent-kit" in markdown
    assert "Score: 88" in markdown
    assert "Packaging signals: deploy, dashboard, integration" in markdown
    assert "## Packaging hypotheses" in markdown
    assert "假设" in markdown
    assert "## Validation checklist" in markdown
    assert "目标用户是谁" in markdown
    assert "7 天内能否做出演示" in markdown
    assert "## Next actions" in markdown


def test_write_opportunity_memo_creates_sanitized_filename(tmp_path: Path) -> None:
    row = _row()
    row["title"] = "demo/agent:kit?"

    output_path = write_opportunity_memo(row, memo_date="2026-05-15", output_dir=tmp_path / "memos")

    assert output_path == tmp_path / "memos" / "2026-05-15-github-123-demo-agent-kit.md"
    assert output_path.read_text(encoding="utf-8").startswith(
        "# Opportunity Memo - demo/agent:kit?"
    )
