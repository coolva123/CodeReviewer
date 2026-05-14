import logging

from src.graph.state import ReviewIssue, ReviewState

logger = logging.getLogger(__name__)


def quality_reviewer_node(state: ReviewState) -> dict:
    """
    Quality Reviewer Agent — 检查代码质量。
    Day 1: 占位实现，返回示例 finding。
    Day 3: 替换为 LLM 调用 + AST 分析集成。
    """
    logger.info("[QualityReviewer] 开始质量审查")

    diff_files = state.get("diff_files", [])

    findings: list[ReviewIssue] = []
    for f in diff_files:
        findings.append({
            "file": f["filename"],
            "line": None,
            "severity": "info",
            "category": "placeholder",
            "title": "[STUB] 质量审查占位",
            "description": f"Day 1 占位: 待 Day 3 实现真实质量分析 (file={f['filename']})",
            "suggestion": "实现 LLM + AST 分析后此条目将被替换",
        })

    msg = f"[QualityReviewer] 完成, 产出 {len(findings)} 条 finding(s)"
    logger.info(msg)

    return {
        "quality_findings": findings,
        "agent_messages": [msg],
    }
