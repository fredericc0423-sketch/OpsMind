from app.graph import graph

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)


def main():

    config = {
        "configurable": {
            "thread_id": "opsmind-001"
        },
        "recursion_limit": 12
    }

    first_round = True

    while True:

        question = input("\nUser: ").strip()

        if question.lower() in ["exit", "quit", "退出"]:
            print("OpsMind 已退出")
            break

        if not question:
            continue

        messages = [
            HumanMessage(content=question)
        ]

        if first_round:
            messages.insert(
                0,
                SystemMessage(
                    content=(
                        "你是 OpsMind 故障诊断 Agent。"
                        "需要时使用监控工具查询数据。"
                        "不要编造监控数据。"
                        "区分可能原因和已确认根因。"
                    )
                )
            )

        try:
            result = graph.invoke(
                {"messages": messages},
                config=config
            )

        except Exception as e:
            print("运行出错:", e)
            continue

        first_round = False

        answer = result["messages"][-1].content

        print("\nOpsMind:")
        print(answer)


if __name__ == "__main__":
    main()