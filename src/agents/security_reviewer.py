import logging

from src.graph.state import ReviewIssue, ReviewState

logger = logging.getLogger(__name__)


def security_reviewer_node(state: ReviewState) -> dict:
    """
    Security Reviewer Agent — 检查安全漏洞。
    Day 1: 占位实现，返回示例 finding。
    Day 3: 替换为 LLM 调用 + bandit 集成。
    """
    logger.info("[SecurityReviewer] 开始安全审查")

    diff_files = state.get("diff_files", [])

    # 占位输出：每个文件生成一条 placeholder finding
    findings: list[ReviewIssue] = []
    for f in diff_files:
        findings.append({
            "file": f["filename"],
            "line": None,
            "severity": "info",
            "category": "placeholder",
            "title": "[STUB] 安全审查占位",
            "description": f"Day 1 占位: 待 Day 3 实现真实安全分析 (file={f['filename']})",
            "suggestion": "实现 LLM + bandit 集成后此条目将被替换",
        })

    msg = f"[SecurityReviewer] 完成, 产出 {len(findings)} 条 finding(s)"
    logger.info(msg)

    return {
        "security_findings": findings,
        "agent_messages": [msg],
    }
