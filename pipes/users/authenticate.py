from __future__ import annotations

from calendar import timegm
from datetime import datetime
from typing import Any

import boto3
import requests
from botocore.exceptions import ClientError
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwk, jwt
from jose.utils import base64url_decode

from pipes.config.settings import settings
from pipes.users.managers import UserManager


class CognitoJWKsVerifier:

    def __init__(self) -> None:
        self._aud = settings.PIPES_COGNITO_CLIENT_ID
        self._keys: dict[str, Any] = {}
        self._iss = f"https://cognito-idp.{settings.PIPES_REGION}.amazonaws.com/{settings.PIPES_COGNITO_USER_POOL_ID}"

    @property
    def jwks_uri(self):
        return f"https://cognito-idp.{settings.PIPES_REGION}.amazonaws.com/{settings.PIPES_COGNITO_USER_POOL_ID}/.well-known/jwks.json"  # noqa: E501

    @property
    def jwks(self):
        if self._keys:
            return self._keys

        response = requests.get(self.jwks_uri).json()
        for key in response["keys"]:
            kid = key["kid"]
            self._keys[kid] = key

        return self._keys

    @property
    def aud(self):
        """JWT Audience"""
        return self._aud

    @property
    def iss(self):
        """JWT Issuer"""
        return self._iss

    def _get_publickey(self, creds: HTTPAuthorizationCredentials):
        try:
            header = jwt.get_unverified_header(creds.credentials)
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid header, not authenticated",
            )

        kid = header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid header, not authenticated",
            )

        try:
            _jwk = self.jwks.get(kid)
            publickey = jwk.construct(_jwk)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid header, not authenticated",
            )
        return publickey

    def _verify_claims(self, creds: HTTPAuthorizationCredentials):
        claims = jwt.get_unverified_claims(creds.credentials)
        try:
            is_verified = jwt.decode(
                token=creds.credentials,
                key="",
                audience=self.aud,
                issuer=self.iss,
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified, expired signature.",
            )
        except jwt.JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified, invalid claims",
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified",
            )

        # verify time
        now = timegm(datetime.utcnow().utctimetuple())

        iat = int(claims.get("iat"))
        if now < iat:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified, invalid iat",
            )

        exp = int(claims.get("exp"))
        if now > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified, expired",
            )

        return is_verified

    def verify_token(self, creds: HTTPAuthorizationCredentials):
        message, signature = creds.credentials.rsplit(".", 1)

        # decode the message and signature
        message = message.encode()
        decoded_signature = base64url_decode(signature.encode())

        publickey = self._get_publickey(creds)
        is_verified = publickey.verify(message, decoded_signature)
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Message Token not verified",
            )

        is_verified = self._verify_claims(creds)

        return is_verified


class CognitoAuth:
    """
    Verify the `access token` and authorize based on scope (or groups)
    """

    async def authenticate(
        self,
        request: Request,
    ) -> HTTPAuthorizationCredentials | None:
        """Authenticate user based Cognito credentials"""
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, _, token = authorization.partition(" ")
        else:
            scheme, token = "", ""

        if not (scheme and token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )

        creds = HTTPAuthorizationCredentials(scheme=scheme, credentials=token)

        verifier = CognitoJWKsVerifier()
        is_verified = verifier.verify_token(creds)
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified.",
            )

        user = None
        return user

    @classmethod
    async def get_current_user(self, creds: HTTPAuthorizationCredentials):
        """Given access token, get current user"""
        cognito_idp = boto3.client("cognito-idp", region_name=settings.PIPES_REGION)

        try:
            response = cognito_idp.get_user(
                AccessToken=creds.credentials,
            )
        except ClientError:
            return None

        username = response["Username"]
        print(username)

        # TODO: find the user
        user = UserManager().get_user_by_email(username)

        return user
