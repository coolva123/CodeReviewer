#!/usr/bin/env python3
"""
MultiAgent Code Reviewer — 入口
用法:
  python main.py --diff-file tests/fixtures/sample.diff
  python main.py --diff-file path/to/your.diff --repo my-org/my-repo
"""
import argparse
import logging
import sys
import uuid
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def parse_args():
    parser = argparse.ArgumentParser(description="MultiAgent Code Reviewer")
    parser.add_argument("--diff-file", required=True, help="Path to unified diff file")
    parser.add_argument("--repo", default="local/repo", help="Repo name (org/repo)")
    parser.add_argument("--pr-title", default="", help="PR title (optional)")
    return parser.parse_args()


def main():
    args = parse_args()

    diff_path = Path(args.diff_file)
    if not diff_path.exists():
        logger.error("Diff file not found: %s", diff_path)
        sys.exit(1)

    diff_content = diff_path.read_text(encoding="utf-8")
    session_id = str(uuid.uuid4())

    logger.info("=" * 60)
    logger.info("MultiAgent Code Reviewer — Day 1 Skeleton")
    logger.info("session_id : %s", session_id)
    logger.info("repo       : %s", args.repo)
    logger.info("diff_file  : %s", diff_path)
    logger.info("=" * 60)

    # Graph import は graph.py 内で build される（モジュールロード時）
    from src.graph.graph import review_graph

    initial_state = {
        "diff_content": diff_content,
        "pr_metadata": {"title": args.pr_title or f"Review of {diff_path.name}"},
        "repo_name": args.repo,
        "session_id": session_id,
        # reducer フィールドは空リストで初期化
        "diff_files": [],
        "routing_decision": {},
        "security_findings": [],
        "quality_findings": [],
        "final_report": None,
        "tool_call_log": [],
        "agent_messages": [],
        "errors": [],
        "current_step": "init",
        "review_complete": False,
    }

    config = {"configurable": {"thread_id": session_id}}

    logger.info("Graph 开始执行 ...")
    result = review_graph.invoke(initial_state, config=config)

    logger.info("=" * 60)
    logger.info("Graph 执行完成")
    logger.info("current_step   : %s", result.get("current_step"))
    logger.info("review_complete: %s", result.get("review_complete"))
    logger.info("diff_files     : %d 个", len(result.get("diff_files", [])))
    logger.info(
        "security_findings: %d 条", len(result.get("security_findings", []))
    )
    logger.info(
        "quality_findings : %d 条", len(result.get("quality_findings", []))
    )
    logger.info("=" * 60)

    report = result.get("final_report", "")
    if report:
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)

    # 验证 checkpointing：恢复状态并检查字段一致性
    logger.info("验证 Checkpointing ...")
    saved = review_graph.get_state(config)
    assert saved.values.get("review_complete") is True, "Checkpointing 验证失败"
    logger.info("Checkpointing 验证通过 ✓")


if __name__ == "__main__":
    main()
