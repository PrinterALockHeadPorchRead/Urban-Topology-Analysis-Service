import sys as _sys
from loguru import logger

def init():
    log_format = "{time}: {level}|\t {message}"
    logger.add(_sys.stderr, format=log_format, level="ERROR")
    logger.add(_sys.stdout, format=log_format, level="INFO")
    logger.add("../logs/logs.log", format=log_format, rotation="1 MB", retention="14 days", level="INFO")
    return logger