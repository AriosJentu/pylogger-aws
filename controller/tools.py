"""
Module for Regular Expressions and Timestamp Manipulation

This module provides functions for working with regular expressions 
and timestamp manipulation.

Functions:
    is_match_name: Checks if a name matches the specified regular expression
                     pattern for container names.
    is_match_name_ws: Checks if a name matches the specified regular 
                        expression pattern for group names.
    mcsecs_to_str: Converts a timestamp in milliseconds to a formatted string.
    get_log_info: Extracts timestamp and message from a log string using 
                  regular expressions.

Requirements:
    - python-dateutil >= 2.8.2
"""

import re
from datetime import datetime
from dateutil import parser
from . import constants

def is_match_name(name: str, expr: str = constants.MATCH_CONTAINER_NAME) -> bool:
    return bool(re.fullmatch(expr, name) and len(name) > 1)

def is_match_name_ws(name: str, expr: str = constants.MATCH_GROUP_NAME) -> bool:
    name = name.replace("#", "")
    return bool(re.fullmatch(expr, name) and len(name) > 1)

def mcsecs_to_str(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp/1000)

def get_log_info(log: str) -> tuple[int, str]:
    regex = re.findall(constants.MATCH_TIMESTAMP_MESSAGE, log)

    if len(regex) == 0:
        raise ValueError("Empty result for expression:", regex, log)

    entry, message = regex[0]
    if entry == "":
        entry, message = message, " "

    timestamp = parser.parse(entry)
    milliseconds = int(timestamp.timestamp() * 1000)
    return milliseconds, message
