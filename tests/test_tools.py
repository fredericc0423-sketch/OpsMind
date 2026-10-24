from app.tools.metrics import get_cpu_metrics
from app.tools.logs import search_logs


# 1. 测试 CPU 查询工具
def test_cpu_metrics():

    result = get_cpu_metrics.invoke({
        "service_name": "order-service"
    })

    assert result["cpu_usage"] == 96.5

    assert result["status"] == "critical"


# 2. 测试不存在的服务
def test_unknown_service():

    result = get_cpu_metrics.invoke({
        "service_name": "unknown-service"
    })

    assert result["error"] == "Service not found"


# 3. 测试日志查询工具
def test_search_logs():

    result = search_logs.invoke({
        "service_name": "order-service"
    })

    assert result["service"] == "order-service"

    assert len(result["logs"]) > 0