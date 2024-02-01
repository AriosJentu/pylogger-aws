"""
Module for AWS-related operations and clients.

This module provides a collection of functions and classes for performing 
various operations related to Amazon Web Services (AWS). It includes methods 
for initializing AWS clients, managing resources, and interacting with 
AWS services such as AWS CloudWatch Logs.


Classes:
    Credentials: A class for storing AWS authentication credentials.
    Configurations: A class for specifying AWS configurations, 
                    such as region and endpoint URL.
    Event: A class for representing AWS CloudWatch log events.
    Group: A class for representing Group in AWS CloudWatch.
    Stream: A class for representing Stream in AWS CloudWatch.
    CloudWatch: A class for interacting with AWS CloudWatch Logs.

Requirements:
    - boto3 >= 1.34.31
"""

import boto3
import os
from . import constants
from . import exceptions
from . import tools

class Credentials:
    """
    Represents AWS credentials for authentication.

    :param aws_access_key_id: The AWS access key ID.
    :param aws_secret_access_key: The AWS secret access key.
    :param aws_session_token: Session token for temporary authentication 
                              (default: without session token).
    """

    def __init__(self, 
            aws_access_key_id: str, 
            aws_secret_access_key: str, 
            aws_session_token: str = ""
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token


class Configurations:
    """
    Represents configurations for AWS services.

    :param region_name: The AWS region name (default: "us-east-1").
    :param endpoint_url: Custom endpoint URL for AWS services 
                         (default: in ENV - AWS_ENDPOINT_URL)
    """

    def __init__(self, 
            region_name: str = "us-east-1", 
            endpoint_url: str = os.getenv("AWS_ENDPOINT_URL")
    ):
        self.region_name = region_name
        self.endpoint_url = endpoint_url

class Event:
    """
    Represents an event with a timestamp, message, and optional ingestion time.

    :param timestamp: The timestamp of the event in milliseconds.
    :param message: The message content associated with the event.
    :param ingestiontime: An optional ingestion time of the event in milliseconds
                          (default: -1, means - not specified).
    """

    def __init__(self, timestamp: int, message: str, ingestiontime: int = -1):
        self.timestamp = timestamp
        self.message = message
        self.ingestiontime = ingestiontime

    @classmethod
    def from_dict(cls, event_dict: dict):
        return cls(
            event_dict.get("timestamp", -1),
            event_dict.get("message", ""),
            event_dict.get("ingestionTime", -1)
        )

    def as_dict(self):
        """
        Create an Event object from a dictionary.

        :param event_dict: A dictionary containing event information.

        :return: An Event object created from the dictionary.
        """
        
        res = {"timestamp": self.timestamp, "message": self.message}
        if self.ingestiontime >= 0:
            res["ingestionTime"] = self.ingestiontime
        return res
    
    def str(self):
        timeinfo = f"[{tools.mcsecs_to_str(self.timestamp)}]"
        
        ingtime = ""
        if self.ingestiontime >= 0:
            ingtime = f"[D - {tools.mcsecs_to_str(self.ingestiontime)}]"

        return f"{timeinfo}{ingtime}: {self.message}"


class Group:
    """
    Represents a group with a name and existence status.

    This class provides a representation of a group with a name and an optional
        existence status.

    :param name: The name of the group.
    """

    def __init__(self, name: str):
        self.__name = name
        self.__exist = None

    def is_exist(self):
        return self.__exist
    
    def set_existence(self, exist: bool = False):
        self.__exist = exist

    @property
    def name(self):
        return self.__name
        

class Stream:
    """
    Represents a stream within a group with a name and existence status.

    This class provides a representation of a stream within a group with a name
    and an optional existence status.

    :param group: The Group object to which this stream belongs.
    :param name: The name of the stream.
    """
    def __init__(self, group: Group, name: str):
        self.__group = group
        self.__name = name
        self.__exist = None

    def is_exist(self):
        return self.__group.is_exist() and self.__exist
    
    def set_existence(self, exist: bool = False):
        if self.__group.is_exist():
            self.__exist = exist

    @property
    def name(self):
        return self.__name


class CloudWatch:
    """
    Represents a client for AWS CloudWatch Logs with optional credentials 
            and configurations.

    This class provides a client for interacting with AWS CloudWatch Logs. 
    It can be initialized with optional AWS credentials and custom 
            configurations.

    :param credentials: An optional Credentials object containing AWS 
                        authentication information. By default loads from 
                        ~/.aws/credentials
    :param configurations: An optional Configurations object specifying AWS 
                           configurations. By default loads from
                           ~/.aws/config
    """

    def __init__(self, 
            credentials: Credentials = None, 
            configurations: Configurations = Configurations()
    ):
        if credentials is not None:
            self.session = boto3.Session(
                aws_access_key_id=credentials.aws_access_key_id,
                aws_secret_access_key=credentials.aws_secret_access_key,
                aws_session_token=credentials.aws_session_token
            )
        else:
            self.session = boto3.Session()

        self.logs_client = self.session.client(
            "logs", 
            endpoint_url=configurations.endpoint_url
        )

    def is_log_group_exist(self, group: Group) -> bool:
        """
        Check if a log group exists.

        :param group: The Group object representing the log group to be checked.

        :return: True if the log group exists, False otherwise.
        """

        exist = group.is_exist()
        if exist is not None:
            return exist
        
        response = self.logs_client.describe_log_groups(
            logGroupNamePrefix=group.name
        )
        exist = len(response["logGroups"]) > 0
        group.set_existence(exist)
        return exist
    
    
    def create_log_group(self, group: Group):
        """
        Create a new log group.

        This method creates a new log group within AWS CloudWatch Logs 
            if it does not already exist.

        :param group: The Group object representing the log group to be created.

        :raises ValueError: If the provided log group name contains 
                            invalid characters.
        :raises AWSLogGroupError: If the log group already exists.
        """

        if not tools.is_match_name_ws(group.name):
            raise ValueError(constants.GROUP_NAME_INCORRECT.format(group.name))
        
        if self.is_log_group_exist(group):
            raise exceptions.AWSLogGroupError(
                constants.GROUP_NAME_EXIST.format(group.name)
            )
        
        self.logs_client.create_log_group(logGroupName=group.name)
        group.set_existence(True)

        
    def is_log_stream_exist(self, group: Group, stream: Stream) -> bool:
        """
        Check if a log stream for chosen log groop exists.

        :param group: The Group object representing the log group to be checked.
        :param stream: The Stream object representing the log stream 
                       to be checked.

        :return: True if the log group exists, False otherwise.
        
        :raises AWSLogGroupError: If the provided log group not found. 
        """

        exist = stream.is_exist()
        if exist is not None:
            return exist
        
        if not self.is_log_group_exist(group):
            raise exceptions.AWSLogGroupError(
                constants.GROUP_NAME_NOT_FOUND.format(group.name)
            )
        
        response = self.logs_client.describe_log_streams(
            logGroupName=group.name, logStreamNamePrefix=stream.name
        )

        exist = len(response["logStreams"]) > 0
        stream.set_existence(exist)
        return exist
    
    
    def create_log_stream(self, group: Group, stream: Stream):
        """
        Create a new log stream within an existing log group.

        :param group: The Group object representing the log group where the 
                      log stream will be created.
        :param stream: The Stream object representing the log stream 
                       to be created.

        :raises AWSLogGroupError: If the specified log group does not exist.
        :raises AWSLogStreamError: If the log stream already exists within 
                                   the log group.
        """

        if not self.is_log_group_exist(group):
            raise exceptions.AWSLogGroupError(
                constants.GROUP_NAME_NOT_FOUND.format(group.name)
            )
        
        if self.is_log_stream_exist(group, stream):
            raise exceptions.AWSLogStreamError(
                constants.STREAM_NAME_EXIST.format(stream.name)
            )

        self.logs_client.create_log_stream(
            logGroupName=group.name,
            logStreamName=stream.name
        )
        stream.set_existence(True)

    def put_log_events(self, 
            group: Group, 
            stream: Stream, 
            events: list[Event]
    ) -> dict:
        
        """
        Put log events into an existing log stream within an existing log group.

        This method sends a list of log events to an existing log stream 
            within an existing log group in AWS CloudWatch Logs.

        :param group: The Group object representing the log group where the 
                      log stream is located.
        :param stream: The Stream object representing the log stream where 
                       events will be placed.
        :param events: A list of Event objects containing the log events 
                       to be sent.

        :return: A dictionary containing information about the operation's 
                 results.
                 
        :raises AWSLogGroupError: If the specified log group does not exist.
        :raises AWSLogStreamError: If the specified log stream does not exist.
        """

        if not self.is_log_group_exist(group):
            raise exceptions.AWSLogGroupError(
                constants.GROUP_NAME_NOT_FOUND.format(group.name)
            )
        
        if not self.is_log_stream_exist(group, stream):
            raise exceptions.AWSLogStreamError(
                constants.STREAM_NAME_NOT_FOUND.format(stream.name)
            )

        return self.logs_client.put_log_events(
            logGroupName=group.name,
            logStreamName=stream.name,
            logEvents=[
                event.as_dict()
                for event in events
            ]
        )
    
    def get_log_events(self, group: str, stream: str) -> list[Event]:
        """
        Retrieve log events from a log stream within a log group.

        This method retrieves log events from a specified log stream within 
            a log group in AWS CloudWatch Logs.

        :param group: The name of the log group where the log stream is located.
        :param stream: The name of the log stream from which to retrieve 
                       log events.

        :return: A list of Event objects representing the retrieved log events.

        :raises AWSLogGroupError: If the specified log group does not exist.
        :raises AWSLogStreamError: If the specified log stream does not exist.
        """

        if not self.is_log_group_exist(group):
            raise exceptions.AWSLogGroupError(
                constants.GROUP_NAME_NOT_FOUND.format(group.name)
            )
        
        if not self.is_log_stream_exist(group, stream):
            raise exceptions.AWSLogStreamError(
                constants.STREAM_NAME_NOT_FOUND.format(group.name)
            )
        
        response = self.logs_client.get_log_events(
            logGroupName=group.name,
            logStreamName=stream.name,
        )

        return [Event.from_dict(e_dict) for e_dict in response["events"]]
