from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def render_opportunity_memo(row: dict[str, Any], memo_date: str) -> str:
    title = str(row.get("title") or row.get("project") or row.get("source_id") or "unknown")
    source = str(row.get("source") or "unknown")
    source_id = str(row.get("source_id") or "unknown")
    packaging_signals = _decode_json_list(row.get("packaging_signals_json"))
    reasons = _decode_json_list(row.get("reasons_json"))
    penalties = _decode_json_list(row.get("penalties_json"))
    hypotheses = _build_packaging_hypotheses(row, packaging_signals)
    next_actions = _build_next_actions(row, packaging_signals, penalties)

    lines = [
        f"# Opportunity Memo - {title}",
        "",
        f"- Generated date: {memo_date}",
        f"- Feedback target: {source} {source_id}",
        "",
        "## Source URL",
        "",
        str(row.get("url") or "unknown"),
        "",
        "## Score snapshot",
        "",
        f"- Score: {row.get('score', 'unknown')}",
        f"- Stars: {row.get('stars', 'unknown')}",
        f"- License: {row.get('license_spdx_id') or 'unknown'}",
        f"- Feedback: {row.get('feedback_status') or 'new'}",
        f"- Packaging signals: {_format_list(packaging_signals)}",
        f"- Reasons: {_format_list(reasons)}",
        f"- Penalties: {_format_list(penalties)}",
        "",
        "## Packaging hypotheses",
        "",
        "下面只是基于公开元数据和扫描信号的保守假设，用来帮助人工讨论，不是结论。",
        "",
    ]
    lines.extend(f"- {hypothesis}" for hypothesis in hypotheses)
    lines.extend(
        [
            "",
            "## Validation checklist",
            "",
            "- 目标用户是谁？先写出一个具体角色，例如独立开发者、运营团队或某个行业的小团队。",
            "- 痛点是什么？用一句话说明他们现在为什么会花时间或钱解决这个问题。",
            "- 原项目为什么不容易直接使用？检查部署、文档、配置、学习成本和维护负担。",
            "- 付费包装能让什么变简单？明确是托管、部署包、模板、集成、本地化还是支持。",
            "- 许可证是否允许计划中的商业包装？在继续前做一次人工 license review。",
            "- 活跃度和维护情况是否足够？查看最近提交、issue 回复和发布节奏。",
            "- 7 天内能否做出演示？如果不能，先缩小到一个可展示的最小场景。",
            "",
            "## Next actions",
            "",
        ]
    )
    lines.extend(f"{index}. {action}" for index, action in enumerate(next_actions, start=1))
    lines.append("")
    return "\n".join(lines)


def write_opportunity_memo(row: dict[str, Any], memo_date: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = _safe_slug(row.get("source") or "unknown")
    source_id = _safe_slug(row.get("source_id") or "unknown")
    title = _safe_slug(row.get("title") or row.get("project") or "opportunity")
    output_path = output_dir / f"{memo_date}-{source}-{source_id}-{title}.md"
    output_path.write_text(render_opportunity_memo(row, memo_date), encoding="utf-8")
    return output_path


def _build_packaging_hypotheses(row: dict[str, Any], signals: list[str]) -> list[str]:
    facts = " ".join(
        [
            str(row.get("title") or ""),
            str(row.get("project") or ""),
            str(row.get("description") or ""),
            " ".join(signals),
        ]
    ).lower()
    hypotheses: list[str] = []

    if _contains_any(facts, ("hosted", "cloud", "self-hosted", "server", "dashboard")):
        hypotheses.append(
            "假设：托管服务可能有价值，因为用户可能想直接使用结果，而不是自己部署和维护。"
        )
    if _contains_any(facts, ("deploy", "docker", "compose", "kubernetes", "terraform", "server")):
        hypotheses.append(
            "假设：部署套件可能有价值，因为公开信号显示安装、部署或运行环境可能是使用门槛。"
        )
    if _contains_any(facts, ("template", "workflow", "dashboard", "agent", "rag")):
        hypotheses.append(
            "假设：垂直场景模板可能有价值，可以把通用项目改造成某类用户能直接套用的方案。"
        )
    if _contains_any(facts, ("integration", "plugin", "api", "workflow", "github")):
        hypotheses.append(
            "假设：集成服务可能有价值，重点验证它能否接入用户已经在用的工具链。"
        )
    if row.get("language") or row.get("license_spdx_id"):
        hypotheses.append(
            "假设：本地化和支持服务可能有价值，但需要先确认目标市场、文档缺口和维护能力。"
        )

    if hypotheses:
        return hypotheses
    return ["假设：当前信号不足，先不要包装；下一步应补充用户、部署难度和使用场景证据。"]


def _build_next_actions(
    row: dict[str, Any],
    signals: list[str],
    penalties: list[str],
) -> list[str]:
    actions = [
        "阅读 README、安装说明和 issue，记录原项目最容易卡住新用户的三个地方。",
        "选定一个目标用户画像，并写出这个用户愿意付费避免的具体麻烦。",
        "做一次人工许可证检查，确认商业包装、托管或分发方式是否可接受。",
    ]
    if signals:
        actions.append("围绕最强的包装信号设计一个 7 天内可完成的小演示。")
    else:
        actions.append("补充包装信号证据；如果找不到明确痛点，就暂缓进入包装实验。")
    if penalties:
        actions.append("逐条复查扣分项，决定它们是可修复风险还是停止条件。")
    elif row.get("feedback_status") == "package":
        actions.append("把该项目列入包装实验候选，并准备一页 demo scope。")
    return actions[:5]


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


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _safe_slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return slug[:80] or "unknown"
