#!/usr/bin/env python
import logging
import colorlog

# Set up a colorful logger
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(cyan)s[%(asctime)s]%(reset)s %(blue)s%(name)s.%(module)s%(reset)s.%(funcName)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'bold_cyan',
        'INFO': 'bold_green',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    }
))
logger = logging.getLogger('test')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Test the logger with different log levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")

# Test with exception
try:
    1/0
except Exception as e:
    logger.exception("An exception occurred")
