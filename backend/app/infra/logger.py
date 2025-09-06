import logging
from logging.handlers import RotatingFileHandler
from app.settings.config import settings

def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Formatter com timestamp e nome do módulo
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # StreamHandler para terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False  # evita logs duplicados com uvicorn
    return logger