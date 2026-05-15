"""
Tool Guard：工具执行保护层 + HITL（Human-in-the-Loop）。

风险分级：
  LOW    — 直接执行
  MEDIUM — 记录日志后执行
  HIGH   — 打印确认提示，等待用户 y/n；非交互模式下自动批准
"""
import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from src.graph.state import ToolCallRecord
from src.harness.memory.short_term import make_tool_record

logger = logging.getLogger(__name__)

_RISK_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "tool_risk_config.yaml"
_risk_cache: dict[str, str] = {}


def _load_risk_config() -> dict[str, str]:
    global _risk_cache
    if _risk_cache:
        return _risk_cache
    with open(_RISK_CONFIG_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    _risk_cache = {name: info["risk_level"] for name, info in raw.get("tools", {}).items()}
    return _risk_cache


def get_risk_level(tool_name: str) -> str:
    """返回工具的风险等级，未配置的工具默认为 MEDIUM。"""
    return _load_risk_config().get(tool_name, "MEDIUM")


def guarded_call(
    tool_fn,
    tool_name: str,
    args: dict[str, Any],
) -> tuple[Any, ToolCallRecord]:
    """
    执行工具并按风险等级控制行为。
    返回 (result, ToolCallRecord)。
    当用户拒绝高风险工具时，result 为 None。
    """
    risk_level = get_risk_level(tool_name)

    if risk_level == "HIGH":
        approved = _prompt_user(tool_name, args)
        if not approved:
            logger.warning("[ToolGuard] HIGH-RISK tool '%s' rejected by user", tool_name)
            record = make_tool_record(tool_name, risk_level, args, result="[REJECTED BY USER]", approved=False)
            return None, record
        logger.info("[ToolGuard] HIGH-RISK tool '%s' approved by user", tool_name)
    elif risk_level == "MEDIUM":
        logger.info("[ToolGuard] MEDIUM-RISK tool '%s' | args_keys=%s", tool_name, list(args.keys()))

    try:
        result = tool_fn.invoke(args)
        result_str = str(result)
        record = make_tool_record(tool_name, risk_level, args, result=result_str[:500], approved=True)
        logger.info(
            "[ToolGuard] '%s' completed | risk=%s | output_len=%d",
            tool_name, risk_level, len(result_str),
        )
        return result, record
    except Exception as exc:
        logger.error("[ToolGuard] Tool '%s' execution error: %s", tool_name, exc)
        record = make_tool_record(tool_name, risk_level, args, result=f"ERROR: {exc}", approved=True)
        return None, record


def _prompt_user(tool_name: str, args: dict[str, Any]) -> bool:
    """终端 HITL 确认提示。非交互模式下自动批准。"""
    print("\n" + "=" * 60, flush=True)
    print("[ToolGuard]  HIGH-RISK TOOL EXECUTION REQUEST", flush=True)
    print(f"  Tool   : {tool_name}", flush=True)
    print(f"  Args   : {_fmt_args(args)}", flush=True)
    print(f"  Reason : This tool spawns a subprocess on your system.", flush=True)
    print("=" * 60, flush=True)

    if not sys.stdin.isatty():
        print("[ToolGuard] Non-interactive mode — auto-approving.", flush=True)
        return True

    while True:
        try:
            answer = input("  Approve execution? [y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter 'y' or 'n'.", flush=True)


def _fmt_args(args: dict[str, Any]) -> str:
    parts = []
    for k, v in args.items():
        v_str = str(v)
        parts.append(f"{k}={v_str[:80]}{'...' if len(v_str) > 80 else ''}")
    return ", ".join(parts)
