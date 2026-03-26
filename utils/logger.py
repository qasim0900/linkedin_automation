import os
import sys
import logging
from logging.handlers import RotatingFileHandler


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
""" 

def setup_logger(
    name="linkedin_automation",
    log_file="logs/app.log",
    level="INFO",
    max_bytes=10 * 1024 * 1024,
    backup_count=5,
):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(fmt)
        console_handler.setLevel(numeric_level)
        logger.addHandler(console_handler)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(numeric_level)
        logger.addHandler(file_handler)
    return logger
