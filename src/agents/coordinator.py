import logging
from datetime import datetime, timezone

from src.graph.state import ReviewState

logger = logging.getLogger(__name__)


def coordinator_node(state: ReviewState) -> dict:
    """
    Coordinator Agent — 任务调度与路由决策。
    Day 1: 占位实现，默认启用所有 Reviewer。
    """
    logger.info("[Coordinator] 开始任务调度")

    repo = state.get("repo_name", "unknown")
    diff_len = len(state.get("diff_content", ""))

    routing_decision = {
        "run_security": True,
        "run_quality": True,
        "reason": f"Default: enable all reviewers for repo={repo}, diff_size={diff_len} chars",
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }

    log_msg = (
        f"[Coordinator] routing_decision={routing_decision}"
    )
    logger.info(log_msg)

    return {
        "routing_decision": routing_decision,
        "current_step": "coordinator_done",
        "agent_messages": [log_msg],
    }
