import logging

from langgraph.graph import END, START, StateGraph

from src.agents.coordinator import coordinator_node
from src.agents.diff_analyzer import diff_analyzer_node
from src.agents.quality_reviewer import quality_reviewer_node
from src.agents.report_generator import report_generator_node
from src.agents.security_reviewer import security_reviewer_node
from src.graph.edges import route_after_coordinator, route_after_diff_analyzer
from src.graph.state import ReviewState
from src.harness.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)


def build_graph():
    """
    构建并编译 ReviewState Graph。

    节点执行顺序：
      START
        └─► coordinator
              └─► diff_analyzer
                    ├─► security_reviewer ─┐
                    └─► quality_reviewer  ─┤
                                           └─► report_generator ─► END
    """
    builder = StateGraph(ReviewState)

    # ── 注册节点 ─────────────────────────────────────────
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("diff_analyzer", diff_analyzer_node)
    builder.add_node("security_reviewer", security_reviewer_node)
    builder.add_node("quality_reviewer", quality_reviewer_node)
    builder.add_node("report_generator", report_generator_node)

    # ── 连接边 ────────────────────────────────────────────
    builder.add_edge(START, "coordinator")

    # Coordinator → DiffAnalyzer（条件路由，支持未来的 early-exit 逻辑）
    builder.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {"diff_analyzer": "diff_analyzer", "__end__": END},
    )

    # DiffAnalyzer → 并行 fan-out 到 Security + Quality Reviewer
    builder.add_conditional_edges(
        "diff_analyzer",
        route_after_diff_analyzer,
        {
            "security_reviewer": "security_reviewer",
            "quality_reviewer": "quality_reviewer",
            "report_generator": "report_generator",
        },
    )

    # 两个 Reviewer 完成后 → ReportGenerator
    builder.add_edge("security_reviewer", "report_generator")
    builder.add_edge("quality_reviewer", "report_generator")

    builder.add_edge("report_generator", END)

    # ── 编译（注入 checkpointer） ─────────────────────────
    checkpointer = get_checkpointer()
    graph = builder.compile(checkpointer=checkpointer)

    logger.info("[Graph] 编译完成，节点: %s", list(builder.nodes))
    return graph


# 模块级单例，供 main.py 直接 import
review_graph = build_graph()
