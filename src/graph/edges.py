from typing import Literal

from .state import ReviewState


def route_after_coordinator(state: ReviewState) -> Literal["diff_analyzer", "__end__"]:
    """Coordinator 决定是否继续审查流程。"""
    if state.get("errors") and not state.get("diff_content"):
        return "__end__"
    return "diff_analyzer"


def route_after_diff_analyzer(
    state: ReviewState,
) -> list[Literal["security_reviewer", "quality_reviewer"]]:
    """
    Diff 分析完成后 fan-out 到 Reviewer。
    Coordinator 的 routing_decision 可以决定跳过某个 Reviewer。
    返回列表让 LangGraph 并行触发多个节点（Send API 替代方案）。
    """
    decision = state.get("routing_decision", {})
    targets = []

    if decision.get("run_security", True):
        targets.append("security_reviewer")
    if decision.get("run_quality", True):
        targets.append("quality_reviewer")

    return targets if targets else ["report_generator"]
