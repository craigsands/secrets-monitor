import boto3
import os
import pytest
import secrets
import uuid

# Get optional environment variables
rotation_lambda_name = os.getenv("ROTATION_LAMBDA_NAME", "secrets-rotator")

# Set the endpoint as required by the handler
os.environ[
    "SECRETS_MANAGER_ENDPOINT"
] = "https://secretsmanager.us-east-1.amazonaws.com"

region = os.environ["AWS_DEFAULT_REGION"]
account_id = boto3.client("sts").get_caller_identity().get("Account")


@pytest.fixture(scope="session")
def client_request_token() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="module")
def secret(client_request_token):
    """Creates a secret to be used by secrets monitor tests"""

    secretsmanager_client = boto3.client(
        "secretsmanager", endpoint_url=os.environ["SECRETS_MANAGER_ENDPOINT"]
    )

    # Create a new secret for testing
    secret_config = {
        "Name": str(uuid.uuid4()),
        "ClientRequestToken": client_request_token,
        "SecretString": secrets.token_hex(32),
    }
    secret = secretsmanager_client.create_secret(**secret_config)
    secretsmanager_client.rotate_secret(
        SecretId=secret["Name"],
        RotationLambdaARN=f"arn:aws:lambda:{region}:{account_id}:function:secrets-rotator",
        RotationRules={"AutomaticallyAfterDays": 90},
        RotateImmediately=False,
    )

    # Pass the secret to each test
    yield secret

    # Delete the secret when finished with it
    secretsmanager_client.delete_secret(
        SecretId=secret["Name"], ForceDeleteWithoutRecovery=True
    )
