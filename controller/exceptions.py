"""
Module for AWS and Docker Exception Definitions

This module defines custom exceptions related to AWS and Docker operations.

Classes:
    ProfileNotFound: Reference to exception AWS ProfileNotFound.
    PartialCredentialsError: Reference to exception AWS PartialCredentialsError.
    NoCredentialsError: Reference to exception AWS NoCredentialsError.
    EndpointConnectionError: Reference to exception AWS EndpointConnectionError.
    ClientError: Reference to exception AWS ClientError.
    DockerImageNotFound: Reference to docker's exception ImageNotFound.
    DockerContainerError: Reference to docker's exception ContainerError.
    DockerAPIError: Reference to docker's exception APIError.
    AWSLogGroupError: Custom exception for AWS CloudWatch Logs 
                      log group-related errors.
    AWSLogStreamError: Custom exception for AWS CloudWatch Logs 
                       log stream-related errors.

Requirements:
    - boto3 >= 1.34.31
    - docker-py >= 7.0.0
"""

import boto3
import docker

ProfileNotFound = boto3.exceptions.botocore.exceptions.ProfileNotFound
PartialCredentialsError = boto3.exceptions.botocore.exceptions.PartialCredentialsError
NoCredentialsError = boto3.exceptions.botocore.exceptions.NoCredentialsError
EndpointConnectionError = boto3.exceptions.botocore.exceptions.EndpointConnectionError
ClientError = boto3.exceptions.botocore.exceptions.ClientError

DockerImageNotFound = docker.errors.ImageNotFound
DockerContainerError = docker.errors.ContainerError
DockerAPIError = docker.errors.APIError

class AWSLogGroupError(Exception):
    pass

class AWSLogStreamError(Exception):
    pass
