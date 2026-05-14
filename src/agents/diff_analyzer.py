import logging
import re

from src.graph.state import DiffFile, ReviewState

logger = logging.getLogger(__name__)


def _parse_diff(raw_diff: str) -> list[DiffFile]:
    """
    简单解析 unified diff，提取每个文件的变更摘要。
    Day 2 会用 LLM + 更精细的解析替换此函数。
    """
    files: list[DiffFile] = []
    current: dict | None = None

    for line in raw_diff.splitlines():
        # 新文件头: --- a/path 或 +++ b/path
        if line.startswith("diff --git "):
            if current:
                files.append(current)  # type: ignore[arg-type]
            # 提取文件名
            match = re.search(r"b/(.+)$", line)
            filename = match.group(1) if match else "unknown"
            current = {
                "filename": filename,
                "change_type": "modified",
                "additions": 0,
                "deletions": 0,
                "patch": "",
            }
        elif line.startswith("new file mode") and current:
            current["change_type"] = "added"
        elif line.startswith("deleted file mode") and current:
            current["change_type"] = "deleted"
        elif current is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current["additions"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                current["deletions"] += 1
            current["patch"] += line + "\n"

    if current:
        files.append(current)  # type: ignore[arg-type]

    return files


def diff_analyzer_node(state: ReviewState) -> dict:
    """
    Diff Analyzer Agent — 解析 diff，生成结构化变更摘要。
    Day 1: 使用轻量规则解析，不调用 LLM。
    """
    logger.info("[DiffAnalyzer] 开始解析 diff")

    diff_content = state.get("diff_content", "")
    diff_files = _parse_diff(diff_content)

    summary = (
        f"[DiffAnalyzer] 解析完成: {len(diff_files)} 个文件变更 "
        f"| 总新增行={sum(f['additions'] for f in diff_files)} "
        f"| 总删除行={sum(f['deletions'] for f in diff_files)}"
    )
    logger.info(summary)

    return {
        "diff_files": diff_files,
        "current_step": "diff_analyzer_done",
        "agent_messages": [summary],
    }
