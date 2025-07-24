import os
import boto3

from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

ROOT_DIR = Path(__file__).parents[1].absolute()
ENV_FILE = ROOT_DIR.joinpath(".env")
load_dotenv(ENV_FILE)

cognito_idp = boto3.client("cognito-idp", region_name="us-west-2")


def get_cognito_access_token():
    """Get Cognit access token for Bearer authentication"""
    response = cognito_idp.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": os.getenv("PIPES_COGNITO_USERNAME"),
            "PASSWORD": os.getenv("PIPES_COGNITO_PASSWORD"),
        },
        ClientId=os.getenv("PIPES_COGNITO_CLIENT_ID"),
    )
    access_token = response["AuthenticationResult"]["AccessToken"]
    export_access_token = f"export PIPES_COGNITO_ACCESS_TOKEN='{access_token}'"
    print(export_access_token)
    return access_token


def create_superuser(access_token):
    """Create superuser at local for development"""
    response = cognito_idp.get_user(
        AccessToken=access_token,
    )
    user_attrs = {
        "username": response["Username"],
        "email": None,
        "first_name": None,
        "last_name": None,
        "organization": "NREL",
        "is_superuser": True,
    }
    for item in response["UserAttributes"]:
        if item["Name"] in user_attrs:
            user_attrs[item["Name"]] = item["Value"]

    mongodb_uri = "mongodb://localhost:27019/"
    client = MongoClient(mongodb_uri)
    db = client["pipes_dev"]

    user = db.users.find_one({"email": user_attrs["email"]})
    if user is not None:
        db.users.update_one({"_id": user["_id"]}, {"$set": {"is_superuser": True}})
    else:
        db.users.insert_one(user_attrs)


if __name__ == "__main__":
    access_token = get_cognito_access_token()
    create_superuser(access_token)
