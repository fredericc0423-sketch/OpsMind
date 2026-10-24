import os

from langchain_ollama import ChatOllama


def get_llm():

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434"
    )

    llm = ChatOllama(
        model="qwen3:8b",
        base_url=base_url,
        temperature=0,
        client_kwargs={
            "trust_env": False,
            "timeout": 120.0
        }
    )

    return llm