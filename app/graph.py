import logging
import time

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

from app.llm import get_llm
from app.tools.metrics import get_cpu_metrics
from app.tools.logs import search_logs
from app.tools.runbook import search_runbook


logger = logging.getLogger("opsmind.graph")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


llm = get_llm()

tools = [
    get_cpu_metrics,
    search_logs,
    search_runbook
]

llm_with_tools = llm.bind_tools(tools)

tool_executor = ToolNode(tools)


def agent_node(state: AgentState):

    start_time = time.perf_counter()

    response = llm_with_tools.invoke(
        state["messages"]
    )

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    tool_names = [
        call["name"]
        for call in response.tool_calls
    ]

    logger.info(
        "llm_finished",
        extra={
            "duration_ms": round(duration_ms, 2),
            "tool_names": tool_names,
            "tool_calls": len(tool_names)
        }
    )

    return {
        "messages": [response]
    }


def tools_node(state: AgentState):

    tool_calls = state["messages"][-1].tool_calls

    tool_names = [
        call["name"]
        for call in tool_calls
    ]

    logger.info(
        "tools_started",
        extra={
            "tool_names": tool_names
        }
    )

    start_time = time.perf_counter()

    try:
        result = tool_executor.invoke(state)

    except Exception:
        logger.exception(
            "tools_failed",
            extra={
                "tool_names": tool_names
            }
        )
        raise

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "tools_finished",
        extra={
            "tool_names": tool_names,
            "duration_ms": round(duration_ms, 2)
        }
    )

    return result


workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)

workflow.add_node("tools", tools_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition
)

workflow.add_edge("tools", "agent")


memory = InMemorySaver()

graph = workflow.compile(
    checkpointer=memory
)