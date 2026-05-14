import logging
from datetime import datetime, timezone

from src.graph.state import ReviewState

logger = logging.getLogger(__name__)


def _severity_emoji(severity: str) -> str:
    return {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵",
        "info": "⚪",
    }.get(severity, "⚪")


def report_generator_node(state: ReviewState) -> dict:
    """
    Report Generator Agent — 汇总所有发现，生成 Markdown 报告。
    Day 1: 生成基础结构的报告，展示骨架跑通。
    Day 6: 替换为 LLM 精化 + formatter.py 美化。
    """
    logger.info("[ReportGenerator] 开始生成报告")

    security_findings = state.get("security_findings", [])
    quality_findings = state.get("quality_findings", [])
    diff_files = state.get("diff_files", [])
    pr_meta = state.get("pr_metadata", {})
    repo_name = state.get("repo_name", "unknown")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Code Review Report",
        f"",
        f"**Repo:** `{repo_name}`  ",
        f"**PR:** {pr_meta.get('title', 'N/A')}  ",
        f"**Generated:** {now}",
        f"",
        f"---",
        f"",
        f"## 变更摘要",
        f"",
        f"共 **{len(diff_files)}** 个文件变更:",
        f"",
    ]
    for f in diff_files:
        lines.append(
            f"- `{f['filename']}` ({f['change_type']}) "
            f"+{f['additions']} / -{f['deletions']}"
        )

    lines += [
        f"",
        f"---",
        f"",
        f"## 安全审查 ({len(security_findings)} 条)",
        f"",
    ]
    for issue in security_findings:
        emoji = _severity_emoji(issue["severity"])
        lines.append(
            f"- {emoji} **[{issue['severity'].upper()}]** `{issue['file']}` — {issue['title']}"
        )
        lines.append(f"  > {issue['description']}")

    lines += [
        f"",
        f"---",
        f"",
        f"## 质量审查 ({len(quality_findings)} 条)",
        f"",
    ]
    for issue in quality_findings:
        emoji = _severity_emoji(issue["severity"])
        lines.append(
            f"- {emoji} **[{issue['severity'].upper()}]** `{issue['file']}` — {issue['title']}"
        )
        lines.append(f"  > {issue['description']}")

    lines += [
        f"",
        f"---",
        f"",
        f"*本报告由 MultiAgent Code Reviewer 自动生成*",
    ]

    report = "\n".join(lines)
    msg = f"[ReportGenerator] 报告生成完成 ({len(report)} chars)"
    logger.info(msg)

    return {
        "final_report": report,
        "review_complete": True,
        "current_step": "done",
        "agent_messages": [msg],
    }
