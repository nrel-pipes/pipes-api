import json
import os
from datetime import datetime, timedelta

import boto3
import pytest
import pytz
from dateutil.parser import parse
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from . import ROOT_DIR

TESTS_DIR = ROOT_DIR.joinpath("tests")

# Environment
TEST_ENV = "testing"
TEST_DOTENV_FILE = str(ROOT_DIR.joinpath(".env.test"))
load_dotenv(TEST_DOTENV_FILE)

# AWS Cognito
TEST_COGNITO_USERNAME = os.getenv("PIPES_COGNITO_TEST_USERNAME")
TEST_COGNITO_PASSWORD = os.getenv("PIPES_COGNITO_TEST_PASSWORD")
TEST_COGNITO_IDP_AUTH_FILE = TESTS_DIR.joinpath("cognito-idp-auth.json")


@pytest.fixture
def pipes_settings(autouse=True):
    from pipes.config.settings import get_settings

    settings = get_settings(TEST_ENV)
    return settings


@pytest.fixture(autouse=True)
def test_client():
    from main import app

    return TestClient(app)


@pytest.fixture
def access_token(pipes_settings):
    """Return Cognit authentication result"""

    auth_result = None

    if TEST_COGNITO_IDP_AUTH_FILE.exists():
        with open(TEST_COGNITO_IDP_AUTH_FILE) as f:
            cached_auth_result = json.load(f)

            # Check if expired
            auth_date = cached_auth_result["ResponseMetadata"]["HTTPHeaders"]["date"]
            expires_in = cached_auth_result["AuthenticationResult"]["ExpiresIn"]

            auth_datetime = parse(auth_date)
            now = datetime.utcnow()
            expiration_datetime = auth_datetime + timedelta(seconds=int(expires_in))
            expiration_datetime = expiration_datetime.astimezone(pytz.utc).replace(
                tzinfo=None,
            )

            if now < expiration_datetime:
                auth_result = cached_auth_result

    # Cognito authentication
    cognito_idp = boto3.client("cognito-idp", region_name=pipes_settings.PIPES_REGION)
    auth_result = cognito_idp.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": TEST_COGNITO_USERNAME,
            "PASSWORD": TEST_COGNITO_PASSWORD,
        },
        ClientId=pipes_settings.PIPES_COGNITO_CLIENT_ID,
    )
    with open(TEST_COGNITO_IDP_AUTH_FILE, "w") as f:
        json.dump(auth_result, f)

    token = auth_result["AuthenticationResult"]["AccessToken"]

    return token
