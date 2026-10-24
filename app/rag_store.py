import os

from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parents[1]

RUNBOOK_PATH = BASE_DIR / "data" / "runbooks.md"

CHROMA_DIR = BASE_DIR / "data" / "chroma_db"


def get_vector_store():

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434"
    )

    embeddings = OllamaEmbeddings(
        model="qwen3-embedding:0.6b",
        base_url=base_url,
        client_kwargs={
            "trust_env": False,
            "timeout": 120.0
        }
    )

    vector_store = Chroma(
        collection_name="opsmind_runbooks",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    return vector_store