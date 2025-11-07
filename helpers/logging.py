import structlog
from pathlib import Path
from datetime import datetime


def create_log(filename: str = "webvtt") -> structlog.BoundLogger:
    log_path = Path(filename).with_suffix(".jsonl")
    if log_path.exists():
        # Append timestamp to the old log file before creating a new one
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = log_path.with_name(
            f"{log_path.stem}_{timestamp}{log_path.suffix}"
        )
        log_path.rename(backup_path)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="ISO", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.EventRenamer("msg"),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(ensure_ascii=False, sort_keys=True),
        ],
        logger_factory=structlog.WriteLoggerFactory(
            file=log_path.open("wt", encoding="utf-8")
        ),
    )
    return structlog.get_logger()
