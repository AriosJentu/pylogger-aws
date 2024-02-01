import argparse
import controller

parser = argparse.ArgumentParser(description="Handler for Docker Container creation.")
parser.add_argument("--docker-image",           help="Name of Docker Image",            required=True)
parser.add_argument("--bash-command",           help="Command for execution in Image",  required=True)
parser.add_argument("--aws-cloudwatch-group",   help="Name of AWS Cloud Watch group",   required=True)
parser.add_argument("--aws-cloudwatch-stream",  help="Name of AWS Cloud Watch stream",  required=True)
parser.add_argument("--aws-access-key-id",      help="The AWS access key ID")
parser.add_argument("--aws-secret-access-key",  help="The AWS secret access key")
parser.add_argument("--docker-container-name",  help="Name of Docker container")
parser.add_argument("--aws-region",             help="The AWS region name")
parser.add_argument("--aws-endpoint",           help="Custom endpoint URL for AWS services")

if __name__ == "__main__":
    args = parser.parse_args()

    interface = controller.interface.Interface(args)
    interface.start()
