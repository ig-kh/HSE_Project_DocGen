import logging
import sys

from api.config import settings


def setup_logger(name: str = settings.LOGGER_NAME) -> logging.Logger:
    """
    Configure application logger.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
