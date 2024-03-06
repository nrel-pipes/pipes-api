from __future__ import annotations

import time
from calendar import timegm
from datetime import datetime
from typing import Any

import boto3
import requests
from botocore.exceptions import ClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwk, jwt
from jose.exceptions import JWTError
from jose.utils import base64url_decode
from pydantic import EmailStr

from pipes.common.constants import DNS_ORG_MAPPING
from pipes.config.settings import settings
from pipes.common import exceptions as E
from pipes.users.contexts import UserManagementContext
from pipes.users.schemas import UserCreate, UserDocument
from pipes.users.managers import UserManager

http_bearer = HTTPBearer()


class CognitoJWKsVerifier:
    """AWS Cognito JWKs Verifier"""

    def __init__(self) -> None:
        self._aud = settings.PIPES_COGNITO_CLIENT_ID
        self._keys: dict[str, Any] = {}
        self._iss = f"https://cognito-idp.{settings.PIPES_REGION}.amazonaws.com/{settings.PIPES_COGNITO_USER_POOL_ID}"
        self._claims: dict[Any, Any] = {}

    @property
    def jwks_url(self):
        return f"https://cognito-idp.{settings.PIPES_REGION}.amazonaws.com/{settings.PIPES_COGNITO_USER_POOL_ID}/.well-known/jwks.json"  # noqa: E501

    @property
    def keys(self):
        if self._keys:
            return self._keys

        response = requests.get(self.jwks_url).json()
        self._keys = {key["kid"]: key for key in response["keys"]}
        return self._keys

    @property
    def aud(self):
        """JWT Audience"""
        return self._aud

    @property
    def iss(self):
        """JWT Issuer"""
        return self._iss

    def _get_publickey(self, access_token: str):
        try:
            headers = jwt.get_unverified_headers(access_token)
        except jwt.JWTError:
            raise E.CognitoAuthError(
                "Not authenticated. Invalid access token - headers.",
            )

        kid = headers.get("kid")
        if not kid:
            raise E.CognitoAuthError("Not authenticated. Invalid access token - kid.")

        try:
            key = self.keys.get(kid)
            publickey = jwk.construct(key)
        except KeyError:
            raise E.CognitoAuthError("Not authenticated. Invalid access token - key.")
        return publickey

    def _verify_claims(self, claims: dict) -> bool:
        # Check token expiration time
        if claims["exp"] < time.time():
            raise E.CognitoAuthError("Not authenticated. Access token expired.")

        # Check issuer client
        if claims["client_id"] != self.aud:
            raise E.CognitoAuthError(
                "Not authenticated. Invalid access token - issuer.",
            )

        # verify issuer auth time
        now = timegm(datetime.utcnow().utctimetuple())
        iat = int(claims.get("iat"))  # type: ignore
        if now < iat:
            raise E.CognitoAuthError("Not authenticated. Invalid access token - iat.")

        self._claims = claims

        return True

    def verify_token(self, access_token: str) -> bool:
        try:
            claims = jwt.get_unverified_claims(access_token)
        except JWTError:
            raise E.CognitoAuthError(
                "Not authenticated. Invalid access token - claims.",
            )

        if claims["token_use"] != "access":
            raise E.CognitoAuthError("Not authenticated. Invalid access token - use.")

        message, signature = str(access_token).rsplit(".", 1)
        decoded_signature = base64url_decode(signature.encode("utf-8"))

        publickey = self._get_publickey(access_token)
        is_verified = publickey.verify(message.encode("utf-8"), decoded_signature)
        if not is_verified:
            raise E.CognitoAuthError(
                "Not authenticated. Invalid access token - not verified.",
            )

        is_verified = self._verify_claims(claims)

        return is_verified


class CognitoAuth:
    """
    Verify the `access token` and authorize based on scope (or groups)
    """

    def __init__(self):
        self.verifier = CognitoJWKsVerifier()

    async def authenticate(
        self,
        auth_creds: HTTPAuthorizationCredentials,
    ) -> UserDocument | None:
        """Authenticate user based Cognito credentials"""
        access_token = auth_creds.credentials

        is_verified = self.verifier.verify_token(access_token)
        if not is_verified:
            return None

        # Get current user
        manager = UserManager(UserManagementContext())
        try:
            cognito_username = self.verifier._claims.get("username")
            user_doc = await manager.get_user_by_username(cognito_username)
        except E.DocumentDoesNotExist:
            cognito_user = await self._get_cognito_user_attributes(access_token)
            if not cognito_user:
                raise E.CognitoAuthError("Invalid access token.")

            organization = await self._parse_organization(cognito_user["email"])
            u_create = UserCreate(
                email=cognito_user["email"],
                first_name=cognito_user["first_name"],
                last_name=cognito_user["last_name"],
                organization=organization,
            )

            try:
                user_doc = await manager.create_user(
                    u_create=u_create,
                    u_username=cognito_user["username"],
                )
            except E.DocumentAlreadyExists:
                pass

        if (not user_doc) or (not user_doc.is_active):
            return None

        current_user = await self._authorize(user_doc)

        return current_user

    async def _authorize(self, user: UserDocument | None) -> UserDocument | None:
        """Authorize user based on scope, group/team, or role"""
        if not user:
            return user

        # TODO: implement logic later if need.

        return user

    async def _get_cognito_user_attributes(self, access_token: str) -> dict | None:
        """Given access token, get current user"""
        cognito_idp = boto3.client("cognito-idp", region_name=settings.PIPES_REGION)
        try:
            response = cognito_idp.get_user(AccessToken=access_token)
        except ClientError:
            return None

        # Get user attributes from Cognito
        user_attrs = {
            "username": response["Username"],
            "email": None,
            "first_name": None,
            "last_name": None,
        }
        for item in response["UserAttributes"]:
            if item["Name"] in user_attrs:
                user_attrs[item["Name"]] = item["Value"]

        return user_attrs

    async def _parse_organization(self, email: EmailStr) -> str | None:
        """Parse organization based on email domain"""
        domain = email.lower().split("@")[1]
        if domain in DNS_ORG_MAPPING:
            return DNS_ORG_MAPPING[domain]
        return None


async def auth_required(
    auth_creds: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    """Authenticate the user and return it"""
    try:
        auth = CognitoAuth()
        user = await auth.authenticate(auth_creds)
    except E.CognitoAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated, exception happened.",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, user None.",
        )
    return user
