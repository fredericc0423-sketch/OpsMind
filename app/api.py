import logging
import time

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from app.graph import graph
from app.logging_config import setup_logging


setup_logging()

logger = logging.getLogger("opsmind.api")


app = FastAPI(
    title="OpsMind API",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    thread_id: str = Field(min_length=1, max_length=128)


class ChatResponse(BaseModel):
    thread_id: str
    answer: str


SYSTEM_PROMPT = (
    "你是 OpsMind 故障诊断 Agent。"
    "请根据监控数据、日志和故障处理手册分析问题。"
    "需要时主动调用工具。"
    "不要编造监控数据。"
    "区分已确认事实和可能原因。"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        logger.exception("http_request_failed")
        raise

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "http_request_finished",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
    )

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        },
        "recursion_limit": 20
    }

    try:
        state = graph.get_state(config)

        history = state.values.get(
            "messages",
            []
        )

        messages = [
            HumanMessage(content=request.question)
        ]

        if not history:
            messages.insert(
                0,
                SystemMessage(content=SYSTEM_PROMPT)
            )

        result = graph.invoke(
            {"messages": messages},
            config=config
        )

        answer = result["messages"][-1].content

        if not isinstance(answer, str):
            answer = str(answer)

        return ChatResponse(
            thread_id=request.thread_id,
            answer=answer
        )

    except Exception as e:

        logger.exception("agent_execution_failed")

        raise HTTPException(
            status_code=500,
            detail="Agent 执行失败，请检查服务日志。"
        ) from e