"""
Module for managing Docker containers and container-related operations.

This module provides classes and functions for managing Docker containers 
and performing various container-related operations. It includes classes 
for creating and managing containers, setting container attributes, 
and checking the existence of Docker images.

Classes:
    Container: Reference to docker's Container.
    ContainerInfo: A class for storing information about a Docker container.
    ContainerCreator: A class for creating and managing Docker containers.

Requirements:
    - docker-py >= 7.0.0
"""

import docker
from . import exceptions 
from . import constants

client = docker.from_env()

Container = docker.models.containers.Container

class ContainerInfo:
    """
    Represents information about a Docker container.

    This class stores information about a Docker container, including its 
    image name, bash command, and name (if specified). 

    :param image_name: The name of the Docker image used for the container.
    :param bash_command: The optional bash command to be executed 
                         in the container.
    :param name: Name assigned to the container 
                 (default: empty, creates by Docker independently).
    """

    def __init__(self, image_name: str, bash_command: str = "", name: str = ""):
        self.image_name = image_name
        self.bash_command = bash_command
        self.name = name

    def get_image_name(self):
        return self.image_name
    
    def get_bash_command(self):
        return self.bash_command

    def get_name(self):
        return self.name

    def set_image_name(self, image_name: str):
        self.image_name = image_name

    def set_name(self, name: str):
        self.name = name


class ContainerCreator:
    """
    Creates and manages Docker containers based on provided 
        container information.

    This class is responsible for creating and managing Docker containers based on the
    provided container information. 

    :param info: A ContainerInfo object containing information about 
                 the container.
    """

    def __init__(self, info: ContainerInfo):
        self.info = info
        self.client = docker.from_env()

    def set_name(self, name: str):
        self.info.set_name(name)

    def set_image_name(self, image_name: str):
        self.info.set_image_name(image_name)

    def is_image_exist(self) -> bool:
        """
        Check if the Docker image exists locally.

        :return: True if the Docker image exists locally, False otherwise.
        """

        local_images = self.client.images.list(filters={
            "reference": self.info.get_image_name()
        })

        return len(local_images) > 0

    def create(self) -> Container:
        """
        Create a new Docker container based on the provided information.

        :return: A Docker container object representing the created container.

        :raises DockerImageNotFound: If the specified Docker image is not found
                                     locally.
        """

        if not self.is_image_exist():
            raise exceptions.DockerImageNotFound(
                constants.IMAGE_NOT_FOUND.format(self.info.get_image_name())
            )
            
        return self.client.containers.create(
            self.info.get_image_name(), 
            command=["/bin/sh", "-c", self.info.get_bash_command()], 
            environment=constants.ENVIRONMENT_VARIABLES,
            name=self.info.get_name()
        )
