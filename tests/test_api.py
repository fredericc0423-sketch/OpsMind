from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import app.api as api_module


# 1. 创建测试客户端
client = TestClient(api_module.app)


# 2. 创建模拟 Agent
@pytest.fixture
def fake_graph(monkeypatch):

    mock_graph = MagicMock()

    mock_graph.get_state.return_value = SimpleNamespace(
        values={}
    )

    mock_graph.invoke.return_value = {
        "messages": [
            AIMessage(content="模拟诊断结果：CPU 使用率异常。")
        ]
    }

    monkeypatch.setattr(
        api_module,
        "graph",
        mock_graph
    )

    return mock_graph


# 3. 测试健康检查接口
def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


# 4. 测试正常对话请求
def test_chat_success(fake_graph):

    request_data = {
        "question": "检查订单服务CPU",
        "thread_id": "test-001"
    }

    response = client.post(
        "/chat",
        json=request_data
    )

    assert response.status_code == 200

    data = response.json()

    assert data["thread_id"] == "test-001"

    assert data["answer"] == "模拟诊断结果：CPU 使用率异常。"

    fake_graph.invoke.assert_called_once()


# 5. 测试已有会话是否避免重复添加系统消息
def test_chat_history(fake_graph):

    fake_graph.get_state.return_value = SimpleNamespace(
        values={
            "messages": [
                HumanMessage(content="上一轮问题")
            ]
        }
    )

    response = client.post(
        "/chat",
        json={
            "question": "继续分析",
            "thread_id": "test-002"
        }
    )

    assert response.status_code == 200

    call_args = fake_graph.invoke.call_args

    messages = call_args.args[0]["messages"]

    assert len(messages) == 1

    assert isinstance(messages[0], HumanMessage)


# 6. 测试首次会话是否添加系统消息
def test_first_message(fake_graph):

    response = client.post(
        "/chat",
        json={
            "question": "检查CPU",
            "thread_id": "test-003"
        }
    )

    assert response.status_code == 200

    call_args = fake_graph.invoke.call_args

    messages = call_args.args[0]["messages"]

    assert isinstance(messages[0], SystemMessage)

    assert isinstance(messages[1], HumanMessage)


# 7. 测试无效输入
def test_invalid_request():

    response = client.post(
        "/chat",
        json={
            "question": "",
            "thread_id": "test-004"
        }
    )

    assert response.status_code == 422


# 8. 测试 Agent 执行失败
def test_agent_error(fake_graph):

    fake_graph.invoke.side_effect = RuntimeError(
        "Internal secret error"
    )

    response = client.post(
        "/chat",
        json={
            "question": "检查CPU",
            "thread_id": "test-005"
        }
    )

    assert response.status_code == 500

    assert "Internal secret error" not in response.text