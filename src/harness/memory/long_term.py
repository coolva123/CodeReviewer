"""
长期记忆：ChromaDB 向量存储封装。
Day 5 实现，此文件为占位骨架。
"""


class LongTermMemory:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self._client = None  # Day 5: chromadb.Client(...)

    def query(self, repo: str, filename: str, top_k: int = 5) -> list[str]:
        """查询历史问题模式（Day 5 实现）。"""
        return []

    def store(self, repo: str, filename: str, findings: list[dict]) -> None:
        """存储审查结果到向量库（Day 5 实现）。"""
        pass
