from secrets_monitor.lambda_function import lambda_handler


def test_rotate_secret(secret, client_request_token):
    """Rotates a secret according to

    https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html#rotate-secrets_how

    """

    secret_id = secret["Name"]

    # Create a new version of the secret
    set_secret_event = {
        "Step": "setSecret",
        "SecretId": secret_id,
        "ClientRequestToken": client_request_token,
    }
    lambda_handler(set_secret_event, context=None)

    # Change the credentials in the database or service
    ...

    # Test the new secret version
    ...

    # Finish the rotation
    finish_secret_event = {
        "Step": "finishSecret",
        "SecretId": secret_id,
        "ClientRequestToken": client_request_token,
    }
    lambda_handler(finish_secret_event, context=None)
