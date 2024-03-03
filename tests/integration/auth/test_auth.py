from __future__ import annotations

from pipes.users.auth import CognitoAuth

from fastapi.security import HTTPAuthorizationCredentials


def test_cognito_auth(cognito_idp_auth_response):

    access_token = cognito_idp_auth_response["AuthenticationResult"]["AccessToken"]
    creds = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=access_token,
    )

    cognito = CognitoAuth()
    cognito.authenticate(creds)
