from langchain_core.tools import tool


@tool
def get_cpu_metrics(service_name: str) -> dict:
    """
    查询指定服务的 CPU 使用率。

    Args:
        service_name: 服务名称，例如 order-service。
    """

    # 模拟监控数据
    metrics = {
        "order-service": 96.5,
        "payment-service": 35.2,
        "user-service": 52.8
    }

    cpu_usage = metrics.get(service_name)

    if cpu_usage is None:
        return {
            "service": service_name,
            "error": "Service not found"
        }

    return {
        "service": service_name,
        "cpu_usage": cpu_usage,
        "unit": "%",
        "status": "critical" if cpu_usage >= 90 else "normal"
    }