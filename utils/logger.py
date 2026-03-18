"""
Logging Configuration

Centralized logging setup for the application.
Logs to both file (with rotation) and console with timestamps.
"""

import logging
import logging.handlers
from pathlib import Path


def setup_logger(
    name: str = "dprs",
    log_level: str = "INFO",
    log_file: str = "logs/app.log",
    max_bytes: int = 10485760,
    backup_count: int = 7
) -> logging.Logger:
    """
    Initialize and return a configured logger instance.

    Args:
        name: Logger name (use __name__ in calling modules)
        log_level: Logging level — INFO, DEBUG, WARNING, ERROR
        log_file: Path to log file (directory created automatically)
        max_bytes: Max file size before rotation (default 10 MB)
        backup_count: Number of rotated backup files to keep

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid duplicate handlers which would cause duplicate logs
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist, to prevent FileNotFoundError
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Define log structure: timestamp, level, logger name, and message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rotating file handler ensures log files don't grow infinitely large
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Module-level default logger
# Module-level default logger — reads settings from config.json if available
def get_logger(name: str = "dprs") -> logging.Logger:
    """Get a logger configured from config.json."""
    try:
        from utils.config import get_config
        config = get_config()
        return setup_logger(
            name=name,
            log_level=config["logging"]["level"],
            log_file=config["logging"]["file"],
            max_bytes=config["logging"]["max_bytes"],
            backup_count=config["logging"]["backup_count"]
        )
    except Exception:
        # If config isn't available, fall back to defaults
        return setup_logger(name)

logger = get_logger()
