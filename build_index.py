from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag_store import get_vector_store, RUNBOOK_PATH


def build_index():

    # 1. 读取故障文档
    text = RUNBOOK_PATH.read_text(encoding="utf-8")

    # 2. 按照章节分割
    sections = text.split("\n---\n")

    documents = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        title = section.splitlines()[0].lstrip("# ").strip()

        document = Document(
            page_content=section,
            metadata={
                "source": "runbooks.md",
                "section": title
            }
        )

        documents.append(document)

    # 3. 将长文档切分成 Chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    # 4. 连接 Chroma
    vector_store = get_vector_store()

    # 5. 清理旧索引，避免重复
    old_ids = vector_store.get()["ids"]

    if old_ids:
        vector_store.delete(ids=old_ids)

    # 6. 向量化并保存到数据库
    vector_store.add_documents(chunks)

    print("知识库索引构建成功！")
    print("文档数量:", len(documents))
    print("Chunk 数量:", len(chunks))


if __name__ == "__main__":
    build_index()