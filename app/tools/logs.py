from langchain_core.tools import tool


@tool
def search_logs(service_name: str) -> dict:
    """查询指定服务的近期异常日志。"""

    logs = {
        "order-service": [
            "ERROR: Database connection timeout",
            "ERROR: Connection pool exhausted",
            "WARN: API response time exceeded 2000ms"
        ],
        "payment-service": [
            "INFO: Service running normally"
        ],
        "user-service": [
            "WARN: Slow database query detected"
        ]
    }

    if service_name not in logs:
        return {
            "service": service_name,
            "error": "Service not found"
        }

    return {
        "service": service_name,
        "logs": logs[service_name]
    }