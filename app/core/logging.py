import json
import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom extra fields if provided, filtering sensitive keys
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            sensitive_keys = {"password", "token", "secret", "authorization", "hashed_password"}
            filtered_extra = {
                k: v for k, v in record.extra_data.items()
                if k.lower() not in sensitive_keys
            }
            log_entry["data"] = filtered_extra

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging():
    logger = logging.getLogger("eve_healthcare")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
