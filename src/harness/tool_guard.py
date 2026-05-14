"""
Tool Guard：工具执行保护层 + HITL（Human-in-the-Loop）。
Day 4 完整实现，此文件为占位骨架。
"""
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}


def guarded_call(
    tool_fn: Callable,
    tool_name: str,
    risk_level: str,
    args: dict[str, Any],
) -> Any:
    """
    根据风险等级决定执行策略：
    - LOW   : 直接执行
    - MEDIUM: 记录日志后执行
    - HIGH  : 暂停并要求用户确认（Day 4 实现）
    """
    if risk_level not in RISK_LEVELS:
        raise ValueError(f"Unknown risk_level: {risk_level}")

    if risk_level == "HIGH":
        # Day 4: 实现真正的 HITL 暂停
        logger.warning("[ToolGuard] HIGH-RISK tool '%s' — HITL not yet implemented, skipping", tool_name)
        return None

    if risk_level == "MEDIUM":
        logger.info("[ToolGuard] MEDIUM-RISK tool '%s' executing with args=%s", tool_name, args)

    return tool_fn(**args)
