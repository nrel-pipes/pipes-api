import os
import boto3

from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1].absolute()
ENV_FILE = ROOT_DIR.joinpath(".env")
load_dotenv(ENV_FILE)


def get_cognito_access_token():
    cognito_idp = boto3.client("cognito-idp", region_name="us-west-2")
    response = cognito_idp.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": os.getenv("PIPES_COGNITO_USERNAME"),
            "PASSWORD": os.getenv("PIPES_COGNITO_PASSWORD"),
        },
        ClientId=os.getenv("PIPES_COGNITO_CLIENT_ID"),
    )
    access_token = response["AuthenticationResult"]["AccessToken"]
    print(access_token)


if __name__ == "__main__":
    get_cognito_access_token()
