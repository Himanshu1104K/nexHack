import logging
from typing import Optional


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    )
    return logging.getLogger(__name__)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the configured format.

    Args:
        name: Logger name (optional, defaults to module name)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


setup_logging()
