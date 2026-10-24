from langchain_core.tools import tool

from app.rag_store import get_vector_store, CHROMA_DIR


@tool
def search_runbook(query: str) -> str:
    """检索故障处理手册，返回相关的故障排查步骤。"""

    # 1. 检查数据库是否存在
    if not CHROMA_DIR.exists():
        return "知识库尚未建立，请先运行 build_index.py"

    # 2. 连接 Chroma
    vector_store = get_vector_store()

    # 3. 检索最相关的两个文本块
    results = vector_store.similarity_search(
        query=query,
        k=2
    )

    if not results:
        return "知识库中没有找到相关内容。"

    # 4. 组织检索结果
    output = []

    for document in results:

        source = document.metadata.get(
            "source",
            "unknown"
        )

        section = document.metadata.get(
            "section",
            "unknown"
        )

        content = document.page_content

        output.append(
            f"来源：{source}\n"
            f"章节：{section}\n"
            f"内容：{content}"
        )

    # 5. 返回给 Agent
    return "\n\n".join(output)