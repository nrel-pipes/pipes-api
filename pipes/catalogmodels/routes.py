from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
)
from pipes.catalogmodels.manager import GeneralCatalogModelManager
from pipes.catalogmodels.schemas import (
    GeneralCatalogModelCreate,
    GeneralCatalogModelRead,
    GeneralCatalogModelUpdate,
)
from pipes.users.auth import auth_required
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/catalogmodel/detail", response_model=GeneralCatalogModelRead, status_code=200)
async def get_catalog_model(
    model_name: str,
    user: UserDocument = Depends(auth_required),
):
    manager = GeneralCatalogModelManager()
    catalogmodel = await manager.get_model(model_name, user)
    return catalogmodel

@router.post("/catalogmodel/create", response_model=GeneralCatalogModelRead, status_code=201)
async def create_catalog_model(
    data: GeneralCatalogModelCreate,
    user: UserDocument = Depends(auth_required),
):
    manager = GeneralCatalogModelManager()
    try:
        mc_doc = await manager.create_model(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    mr_doc = await manager.read_model(mc_doc)
    return mr_doc

@router.get("/catalogmodels", response_model=list[GeneralCatalogModelRead], status_code=200)
async def get_catalog_models(
    user: UserDocument = Depends(auth_required),
):
    manager = GeneralCatalogModelManager()
    catalogmodels = await manager.get_models(user)
    return catalogmodels

@router.patch("/catalogmodel/update", response_model=GeneralCatalogModelRead, status_code=200)
async def update_catalog_model(
    model_name: str,
    data: GeneralCatalogModelUpdate,
    user: UserDocument = Depends(auth_required),
):
    user_manager = UserManager()
    user_ids = []
    for email in data.access_group:
        try:
            user_doc = await user_manager.get_user_by_email(email)
        except DocumentDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{email}' does not exist.",
            )
        user_ids.append(user_doc.id)
    data.access_group = user_ids

    manager = GeneralCatalogModelManager()
    try:
        updated_model = await manager.update_model(model_name, data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return updated_model

@router.delete("/catalogmodel/delete", status_code=204)
async def delete_catalog_model(
    model_name: str,
    user: UserDocument = Depends(auth_required),
):
    manager = GeneralCatalogModelManager()
    try:
        await manager.delete_model(model_name, user)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return None
