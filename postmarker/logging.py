# coding: utf-8
from __future__ import absolute_import

import logging


DEFAULT_LOGGING_LEVEL = logging.CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def get_logger(name, verbosity):
    """
    Returns simple console logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel({
        0: DEFAULT_LOGGING_LEVEL,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(min(2, verbosity), DEFAULT_LOGGING_LEVEL))
    logger.handlers = []
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger
