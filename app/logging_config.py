import json
import logging
import sys

from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):

    def format(self, record):

        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage()
        }

        extra_fields = [
            "method",
            "path",
            "status_code",
            "duration_ms",
            "tool_names",
            "tool_calls"
        ]

        for field in extra_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        if record.exc_info:
            log_data["traceback"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def setup_logging():

    logger = logging.getLogger("opsmind")

    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)

    logger.setLevel(logging.INFO)

    logger.propagate = False