from __future__ import annotations

from pipes.accessgroups.manager import AccessGroupManager
from pipes.accessgroups.schemas import (
    AccessGroupCreate,
    AccessGroupRead,
    AccessGroupUpdate,
)
from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.document import DocumentDB
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


# Access Groups
@router.post("/accessgroups", response_model=AccessGroupRead, status_code=201)
async def create_accessgroup(
    data: AccessGroupCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new access group"""
    try:
        manager = AccessGroupManager()
        ag_doc = await manager.create_accessgroup(data)
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Query members
    docdb = DocumentDB()
    u_docs = await docdb.find_all(
        collection=UserDocument,
        query={"_id": {"$in": ag_doc.members}},
    )

    ag_read = AccessGroupRead(
        name=ag_doc.name,
        description=ag_doc.description,
        members=u_docs,
    )

    return ag_read


@router.get("/accessgroups", response_model=list[AccessGroupRead])
async def get_accessgroups(
    user: UserDocument = Depends(auth_required),
):
    """Get all access groups"""
    manager = AccessGroupManager()
    accessgroups = await manager.get_all_accessgroups()
    return accessgroups


@router.get("/accessgroups/detail", response_model=AccessGroupRead)
async def get_accessgroup(
    accessgroup: str,
    user: UserDocument = Depends(auth_required),
):
    """Get a specific access group by name"""
    try:
        manager = AccessGroupManager()
        ag_doc = await manager.get_accessgroup(accessgroup)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    # Query members
    docdb = DocumentDB()
    u_docs = await docdb.find_all(
        collection=UserDocument,
        query={"_id": {"$in": ag_doc.members}},
    )

    ag_read = AccessGroupRead(
        name=ag_doc.name,
        description=ag_doc.description,
        members=u_docs,
    )

    return ag_read


@router.patch("/accessgroups")
async def update_accessgroup(
    accessgroup: str,
    data: AccessGroupUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update access group"""
    try:
        manager = AccessGroupManager()
        ag_doc = await manager.update_accessgroup(accessgroup, data)
    except (DocumentDoesNotExist, DocumentAlreadyExists) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    docdb = DocumentDB()
    u_docs = await docdb.find_all(
        collection=UserDocument,
        query={"_id": {"$in": ag_doc.members}},
    )
    ag_read = AccessGroupRead(
        name=ag_doc.name,
        description=ag_doc.description,
        members=u_docs,
    )
    return ag_read


@router.delete("/accessgroups", status_code=204)
async def delete_accessgroup(
    accessgroup: str,
    user: UserDocument = Depends(auth_required),
):
    """Delete a specific access group by name"""
    try:
        manager = AccessGroupManager()
        await manager.delete_accessgroup(accessgroup)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
