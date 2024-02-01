"""
Module for storing constants and messages used in the application.

This module contains constants and messages that are used throughout the 
application to maintain consistency and facilitate localization of messages.
"""

IMAGE_NOT_FOUND = "Image not found on local machine. Please install it using \"docker pull {}\""

STRING_DOESN_MATCH = "String doesn't match given regular expression"
POSITIVE_INTEGER = "Should be positive integer values"
NOT_IN_RANGE = "Value not in fixed range"
INCORRECT_ANSWER = "Incorrect answer"
INTERRUPTION_STRING = "Interruption. Close interface!"

GROUP_NAME_INCORRECT = "Group name '{}' is incorrect. Log group names consist of the following characters: a-z, A-Z, 0-9, '_', '-', '/', '.', and '#'"
GROUP_NAME_EXIST = "Group name '{}' already exist"
GROUP_NAME_NOT_FOUND = "Group name '{}' not found"
STREAM_NAME_EXIST = "Stream name '{}' already exist"
STREAM_NAME_NOT_FOUND = "Stream name '{}' not found"

MATCH_CONTAINER_NAME = r"[a-zA-Z0-9][a-zA-Z0-9_.-]+"
MATCH_GROUP_NAME = r"[a-zA-Z0-9][a-zA-Z0-9_.-/]+[a-zA-Z0-9_.-]"
MATCH_TIMESTAMP_MESSAGE = r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?[0-9]*(?:Z|z))?\s*(.+)"

ENVIRONMENT_VARIABLES = {
    "PYTHONUNBUFFERED": 1
}
