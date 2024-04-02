from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    DocumentDoesNotExist,
    DocumentAlreadyExists,
    VertexAlreadyExists,
)
from pipes.common.utilities import parse_organization
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel
from pipes.graph.schemas import UserVertexProperties, UserVertex
from pipes.users.schemas import UserCreate, CognitoUserCreate, UserDocument

logger = logging.getLogger(__name__)


class UserManager(AbstractObjectManager):
    """Manager class for user management"""

    __label__ = VertexLabel.User.value

    async def create_user(
        self,
        u_create: UserCreate | CognitoUserCreate,
    ) -> UserDocument:
        """Admin create new user"""
        u_vertex = await self._create_user_vertex(u_create.email)
        return await self._create_user_document(u_create, u_vertex)

    async def _get_user_vertex(self, email: EmailStr) -> UserVertex | None:
        vlist = self.n.get_v(self.label, email=email)
        if not vlist:
            return None

        u_vtx = vlist[0]
        properties_model = UserVertexProperties(email=email)
        user_vertex_model = UserVertex(
            id=u_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return user_vertex_model

    async def _create_user_vertex(self, email: EmailStr) -> UserVertex | None:
        if self.n.exists(self.label, email=email):
            raise VertexAlreadyExists(f"User vertex ({email}) already exists.")

        properties_model = UserVertexProperties(email=email)
        properties = properties_model.model_dump()
        u_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        user_vertex_model = UserVertex(
            id=u_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return user_vertex_model

    async def _get_or_create_user_vertex(self, email: EmailStr) -> UserVertex:
        properties_model = UserVertexProperties(email=email)
        properties = properties_model.model_dump()

        u_vtx = self.n.get_or_add_v(self.label, **properties)

        user_vertex_model = UserVertex(
            id=u_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return user_vertex_model

    async def _create_user_document(self, u_create, u_vertex):
        # Check if user already exists
        exists = await self.d.exists(
            collection=UserDocument,
            query={"email": u_create.email},
        )
        if exists:
            raise DocumentAlreadyExists(
                f"User document ({u_create.email}) already exists.",
            )

        username = getattr(u_create, "username", None)

        organization = u_create.organization
        if not organization:
            organization = parse_organization(u_create.email)

        u_doc = UserDocument(
            vertex=u_vertex,
            username=username,
            email=u_create.email,
            first_name=u_create.first_name,
            last_name=u_create.last_name,
            organization=u_create.organization,
            created_at=datetime.now(),
            is_active=True,
            is_superuser=False,
        )

        try:
            await self.d.insert(u_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(f"User '{u_create.email}' already exists.")
        return u_doc

    async def get_or_create_user(self, u_create: UserCreate) -> UserDocument:
        """Get or create user"""
        u_doc = await self.d.find_one(
            collection=UserDocument,
            query={"email": u_create.email},
        )
        if u_doc:
            return u_doc

        # Create a new user
        organization = u_create.organization
        if not organization:
            organization = parse_organization(u_create.email)

        u_vertex = await self._get_or_create_user_vertex(u_create.email)

        u_doc = UserDocument(
            vertex=u_vertex,
            email=u_create.email,
            first_name=u_create.first_name,
            last_name=u_create.last_name,
            organization=organization,
            created_at=datetime.now(),
        )
        u_doc = await self.d.insert(u_doc)
        return u_doc

    async def get_all_users(self) -> list[UserDocument]:
        """Admin get all users from documentdb"""
        u_docs = await self.d.find_all(collection=UserDocument)
        return u_docs

    async def get_user_by_email(self, email: EmailStr) -> UserDocument:
        """Get user by email"""
        email = email.lower()
        u_doc = await self.d.find_one(collection=UserDocument, query={"email": email})
        if not u_doc:
            raise DocumentDoesNotExist(f"User '{email}' not found")
        return u_doc

    async def get_user_by_username(self, username: str) -> UserDocument:
        """Get user by cognito username decoded from access token"""
        u_doc = await self.d.find_one(
            collection=UserDocument,
            query={"username": username},
        )
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - username: {username}")
        return u_doc

    async def get_user_by_id(self, id: PydanticObjectId) -> UserDocument:
        """Get user by document id"""
        u_doc = await self.d.get(collection=UserDocument, id=id)
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - user id: {id}")
        return u_doc
