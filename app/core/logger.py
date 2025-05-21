import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    formatter = logging.Formatter(fmt)

    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    handlers = [
        RotatingFileHandler(
            "logs/app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)