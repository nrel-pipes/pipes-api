from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
)
from pipes.catalogdatasets.manager import CatalogDatasetManager
from pipes.catalogdatasets.schemas import (
    CatalogDatasetCreate,
    CatalogDatasetRead,
    CatalogDatasetUpdate,
)
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/catalogdataset/detail",
    response_model=CatalogDatasetRead,
    status_code=200,
)
async def get_catalog_dataset(
    dataset_name: str,
    user: UserDocument = Depends(auth_required),
):
    manager = CatalogDatasetManager()
    catalogdataset = await manager.get_dataset(dataset_name, user)
    return catalogdataset


@router.post(
    "/catalogdataset/create",
    response_model=CatalogDatasetRead,
    status_code=201,
)
async def create_catalog_dataset(
    data: CatalogDatasetCreate,
    user: UserDocument = Depends(auth_required),
):
    manager = CatalogDatasetManager()
    try:
        cd_doc = await manager.create_dataset(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    cd_read = await manager.read_dataset(cd_doc)
    return cd_read


@router.get(
    "/catalogdatasets",
    response_model=list[CatalogDatasetRead],
    status_code=200,
)
async def get_catalog_datasets(
    user: UserDocument = Depends(auth_required),
):
    manager = CatalogDatasetManager()
    catalogdatasets = await manager.get_datasets(user)
    return catalogdatasets


@router.patch(
    "/catalogdataset/update",
    response_model=CatalogDatasetRead,
    status_code=200,
)
async def update_catalog_dataset(
    dataset_name: str,
    data: CatalogDatasetUpdate,
    user: UserDocument = Depends(auth_required),
):
    manager = CatalogDatasetManager()
    try:
        updated_dataset = await manager.update_dataset(dataset_name, data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return updated_dataset


@router.delete("/catalogdataset/delete", status_code=204)
async def delete_catalog_dataset(
    dataset_name: str,
    user: UserDocument = Depends(auth_required),
):
    manager = CatalogDatasetManager()
    try:
        await manager.delete_dataset(dataset_name, user)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return None
