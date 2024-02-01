# Docker Container Logger for AWS CloudWatch on Python

## Introduction

The **Docker Container Logger for AWS CloudWatch** is a Python program designed to create and manage Docker containers, capture their output logs, and send those logs to AWS CloudWatch. This tool simplifies the process of logging Docker container output to a CloudWatch group and stream.

Key Features:
- Create a Docker container using a specified Docker image (which should be installed on local machine) and bash command.
- Capture the output logs of the Docker container.
- Send container logs to AWS CloudWatch in a specified log group and stream.
- Create the CloudWatch log group and stream if they do not exist.
- Supports customization of AWS credentials, region, and endpoint URL.

## Usage

To use the program, you can run it from the command line with the following arguments:

```shell
python main.py --docker-image <DOCKER_IMAGE_NAME> --bash-command <BASH_COMMAND> --docker-container-name <CONTAINER_NAME> --aws-cloudwatch-group <LOG_GROUP_NAME> --aws-cloudwatch-stream <LOG_STREAM_NAME> --aws-access-key-id <ACCESS_KEY_ID> --aws-secret-access-key <SECRET_ACCESS_KEY> --aws-region <AWS_REGION> --aws-endpoint <AWS_ENDPOINT_URL>
```

### Example
LocalStack Example:
```shell
python main.py --docker-image python --bash-command $'pip install pip -U && pip install tqdm && python -c \"import time\ncounter = 0\nfor i in range(100):\n\tprint(counter)\n\tcounter = counter + 1\n\ttime.sleep(0.1)\"' --docker-container-name "example" --aws-cloudwatch-group LogGroup --aws-cloudwatch-stream LogStream --aws-access-key-id "LSIAQAAAAAAVNCBMPNSG" --aws-secret-access-key "" --aws-region "us-east-1" --aws-endpoint "http://localhost.localstack.cloud:4566"
```

## Requirements

To run the program, you need to install the following Python packages:

- **docker-py** >= 7.0.0
- **boto3** >= 1.34.31
- **python-dateutil** >= 2.8.2

You can install these packages using pip:

```shell
pip install docker-py boto3 python-dateutil
```

## License

This project is licensed under the [MIT License](LICENSE).