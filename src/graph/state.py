import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class DiffFile(TypedDict):
    filename: str
    change_type: str          # "added" | "modified" | "deleted"
    additions: int
    deletions: int
    patch: str                # raw unified diff for this file


class ReviewIssue(TypedDict):
    file: str
    line: Optional[int]
    severity: str             # "critical" | "high" | "medium" | "low" | "info"
    category: str
    title: str
    description: str
    suggestion: str


class ToolCallRecord(TypedDict):
    tool_name: str
    risk_level: str
    args: Dict[str, Any]
    result: Optional[str]
    approved: bool
    timestamp: str


class ReviewState(TypedDict):
    # ── 输入 ─────────────────────────────────────────────
    diff_content: str
    pr_metadata: Dict[str, Any]   # title, description, author, url 等
    repo_name: str
    session_id: str

    # ── Agent 输出（逐步填充） ────────────────────────────
    diff_files: List[DiffFile]                              # DiffAnalyzer 输出
    routing_decision: Dict[str, Any]                        # Coordinator 路由决策

    # 用 operator.add reducer：并行节点各自 append，LangGraph 自动合并
    security_findings: Annotated[List[ReviewIssue], operator.add]
    quality_findings: Annotated[List[ReviewIssue], operator.add]

    final_report: Optional[str]                             # ReportGenerator 输出

    # ── Harness 层 ────────────────────────────────────────
    tool_call_log: Annotated[List[ToolCallRecord], operator.add]
    agent_messages: Annotated[List[str], operator.add]      # 各节点的执行日志
    errors: Annotated[List[str], operator.add]

    # ── 控制流 ────────────────────────────────────────────
    current_step: str
    review_complete: bool
