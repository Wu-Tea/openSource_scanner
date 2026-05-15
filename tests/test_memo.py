from __future__ import annotations

from pathlib import Path

import pytest

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

    assert "# 机会备忘录 - demo/agent-kit" in markdown
    assert "生成日期: 2026-05-15" in markdown
    assert "反馈目标: github 123" in markdown
    assert "https://github.com/demo/agent-kit" in markdown
    assert "## 来源链接" in markdown
    assert "## 评分快照" in markdown
    assert "分数: 88" in markdown
    assert "包装信号: deploy, dashboard, integration" in markdown
    assert "## 包装假设" in markdown
    assert "假设" in markdown
    assert "## 验证清单" in markdown
    assert "目标用户是谁" in markdown
    assert "7 天内能否做出演示" in markdown
    assert "## 下一步行动" in markdown


def test_write_opportunity_memo_creates_sanitized_filename(tmp_path: Path) -> None:
    row = _row()
    row["title"] = "demo/agent:kit?"

    output_path = write_opportunity_memo(row, memo_date="2026-05-15", output_dir=tmp_path / "memos")

    assert output_path == tmp_path / "memos" / "2026-05-15-github-123-demo-agent-kit.md"
    assert output_path.read_text(encoding="utf-8").startswith("# 机会备忘录 - demo/agent:kit?")


def test_write_opportunity_memo_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    output_dir = tmp_path / "memos"
    output_path = write_opportunity_memo(_row(), memo_date="2026-05-15", output_dir=output_dir)
    output_path.write_text("human edits", encoding="utf-8")

    with pytest.raises(FileExistsError, match="already exists"):
        write_opportunity_memo(_row(), memo_date="2026-05-15", output_dir=output_dir)

    assert output_path.read_text(encoding="utf-8") == "human edits"

    forced_path = write_opportunity_memo(
        _row(),
        memo_date="2026-05-15",
        output_dir=output_dir,
        force=True,
    )

    assert forced_path == output_path
    assert forced_path.read_text(encoding="utf-8").startswith("# 机会备忘录 - demo/agent-kit")
