"""
Interface for Managing AWS CloudWatch and Docker Operations

This class represents an interface for managing AWS CloudWatch and 
Docker operations. It provides methods for creating and starting 
Docker containers, monitoring container events, and sending log events 
to AWS CloudWatch.

Classes:
    Interface: High-level interface for managing AWS CloudWatch 
               and Docker operations.
"""

import argparse
from . import exceptions
from . import tools
from . import container
from . import aws

class Interface:
    """
    Interface for Managing AWS CloudWatch and Docker Operations.

    Parameters:
        :param args: Command-line arguments parsed using argparse.
    """

    def __init__(self, arguments: argparse.Namespace):
        self.args = arguments
        self.group = aws.Group(self.args.aws_cloudwatch_group)
        self.stream = aws.Stream(self.group, self.args.aws_cloudwatch_stream)

    @classmethod
    def exit(cls, exception: Exception):
        print(":::", exception)
        exit()

    def create_container(self) -> container.Container:
        """
        Create a Docker container based on provided container information.

        This method creates and configures a Docker container using the 
            specified container information, which includes the Docker image, 
            bash command, and container name.

        :return: An instance of the container.Container class representing 
                 the created Docker container.

        :raises DockerImageNotFound: If the specified Docker image 
                                      is not found locally.
        :raises DockerContainerError: If an error occurs during 
                                       container creation or configuration.
        :raises DockerAPIError: If an error occurs while interacting 
                                 with the Docker API.
        """

        container_info = container.ContainerInfo(
            image_name=self.args.docker_image,
            bash_command=self.args.bash_command,
            name=self.args.docker_container_name
        )

        creator = container.ContainerCreator(container_info)

        try:
            return creator.create()
        except (
                exceptions.DockerImageNotFound,
                exceptions.DockerContainerError,
                exceptions.DockerAPIError
        ) as ex: 
            Interface.exit(ex)


    def start_container(self, container: container.Container):
        """
        Start a Docker container.

        This method starts the specified Docker container, allowing 
            it to run and produce log events.

        :param container: An instance of the container.Container class 
                          representing the Docker container to start.

        :raises DockerAPIError: If an error occurs while starting 
                                 the Docker container.
        """

        try:
            container.start()
        except exceptions.DockerAPIError as ex:
            Interface.exit(ex)


    def container_events(self, container: container.Container) -> aws.Event:
        """
        Generate events from the Docker container's logs.

        This method reads and processes log data from the specified Docker 
            container's logs in real-time. It generates log events as instances 
            of the aws.Event class, which include a timestamp and log message.

        :param container: An instance of the container.Container class 
                          representing the Docker container.

        :return: A generator that yields aws.Event objects representing 
                 log events.
        """

        for log in container.logs(stream=True, follow=True, timestamps=True):
            log_data = log.decode("utf-8").strip()
            time, message = tools.get_log_info(log_data)
            yield aws.Event(time, message)

    
    def create_cloudwatch_object(self) -> aws.CloudWatch:
        """
        Create an AWS CloudWatch client object.

        This method creates an instance of the aws.CloudWatch class, 
            configured with AWS credentials and CloudWatch endpoint details 
            for log event transmission.

        :return: An instance of the aws.CloudWatch class for interacting 
                 with AWS CloudWatch.

        :raises NoCredentialsError: If AWS credentials are not provided 
                 or incomplete.
        :raises PartialCredentialsError: If AWS credentials are incomplete.
        :raises ProfileNotFound: If the specified AWS profile is not found.
        :raises EndpointConnectionError: If there is an issue connecting 
                 to the specified CloudWatch endpoint.
        :raises ClientError: If an AWS client error occurs.
        """
            
        credentials = aws.Credentials(
            aws_access_key_id=self.args.aws_access_key_id,
            aws_secret_access_key=self.args.aws_secret_access_key
        )

        config = aws.Configurations(
            region_name=self.args.aws_region,
            endpoint_url=self.args.aws_endpoint
        )

        try:
            return aws.CloudWatch(credentials, config)
        except (
            exceptions.NoCredentialsError,
            exceptions.PartialCredentialsError,
            exceptions.ProfileNotFound,
            exceptions.EndpointConnectionError,
            exceptions.ClientError
        ) as ex:
            Interface.exit(ex)

    
    def make_cloudwatch_group(self, cloudwatch: aws.CloudWatch) -> bool:
        """
        Create a CloudWatch log group if it does not exist.

        This method checks if the specified CloudWatch log group exists. 
            If it does not exist, it attempts to create the log group using 
            the provided aws.CloudWatch client object.

        :param cloudwatch: An instance of the aws.CloudWatch class 
                           for interacting with AWS CloudWatch.

        :return: True if the CloudWatch log group was created, False if 
                 the log group already exists.

        :raises ValueError: If there is an issue with the log group name 
                            format.
        :raises ClientError: If an AWS client error occurs while creating 
                             the log group.
        """

        if not cloudwatch.is_log_group_exist(self.group):
            try:
                cloudwatch.create_log_group(self.group)
                return True
            
            except (
                ValueError,
                exceptions.ClientError
            ) as ex:
                Interface.exit(ex)

        return False

    def make_cloudwatch_stream(self, cloudwatch: aws.CloudWatch) -> bool:
        """
        Create a CloudWatch log stream if it does not exist.

        This method checks if the specified CloudWatch log stream exists 
            within the provided CloudWatch log group. If the log stream 
            does not exist, it attempts to create the log stream using 
            the provided aws.CloudWatch client object.

        :param cloudwatch: An instance of the aws.CloudWatch class 
                           for interacting with AWS CloudWatch.

        :return: True if the CloudWatch log stream was created, False if 
                 the log stream already exists.

        :raises ValueError: If there is an issue with the log stream name 
                            format.
        :raises ClientError: If an AWS client error occurs while creating 
                             the log stream.
        """
            
        if not cloudwatch.is_log_stream_exist(self.group, self.stream):
            try:
                cloudwatch.create_log_stream(self.group, self.stream)
                return True
            
            except (
                ValueError,
                exceptions.ClientError
            ) as ex:
                Interface.exit(ex)

        return False

    def put_log_event(self, cloudwatch: aws.CloudWatch, event: aws.Event):
        """
        Put a log event into a CloudWatch log stream.

        This method puts a log event, represented by an aws.Event object, 
            into the specified CloudWatch log stream within the corresponding 
            log group.

        :param cloudwatch: An instance of the aws.CloudWatch class 
                           for interacting with AWS CloudWatch.
        :param event: An aws.Event object representing the log event 
                      to be added to the log stream.

        :raises: ClientError: If an AWS client error occurs 
                              while putting the log event.
        """
            
        try:
            cloudwatch.put_log_events(self.group, self.stream, [event])

        except exceptions.ClientError as ex:
            Interface.exit(ex)

    def start(self):
        """
        Start the entire logging process.

        This method orchestrates the entire logging process, including 
            creating and starting a Docker container, establishing a connection 
            to AWS CloudWatch, creating CloudWatch log groups and streams, 
            and continuously monitoring the Docker container's logs 
            to send log events to CloudWatch.

        :raises: KeyboardInterrupt: If the user interrupts the logging process.
        :raises: EOFError: If there is an issue with input/output during the 
                           logging process, or Ctrl-D.
        :raises: ClientError: If an AWS client error occurs during any 
                              of the CloudWatch operations.
        """

        try:

            cloudwatch = self.create_cloudwatch_object()
            print("::: Connection to CloudWatch established")

            grp = self.make_cloudwatch_group(cloudwatch)
            print(f"::: CloudWatch group {'created' if grp else 'found'}")

            stm = self.make_cloudwatch_stream(cloudwatch)
            print(f"::: CloudWatch stream {'created' if stm else 'found'}")

            docker_container = self.create_container()
            print("::: Container created")

            self.start_container(docker_container)
            print("::: Container started")

            for event in self.container_events(docker_container):
                print(event.str())
                self.put_log_event(cloudwatch, event)
        
        except (KeyboardInterrupt, EOFError, exceptions.ClientError) as ex:
            Interface.exit(ex)
