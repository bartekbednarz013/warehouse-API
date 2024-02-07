from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from dependencies import get_db
from models.part import PartModel, PartCreateModel, PartListModel, PartUpdateModel
from crud.part import create_part, read_part, update_part, delete_part, read_parts, PartSerialNumberAlreadyExistsError, InvalidPartIDError
from crud.category import read_category_by_name


router = APIRouter(prefix="/part", tags=["part"])


@router.post("", response_model=PartModel, status_code=status.HTTP_201_CREATED)
async def add_part(part: PartCreateModel, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    await _validate_category(db, part.category)
    try:
        created_part = await create_part(db, part)
    except PartSerialNumberAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Part with this serial number already exists.")
    return created_part


@router.get("/{part_id}/", response_model=PartModel)
async def get_part(part_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    part = await _get_part(db, part_id)
    return part


@router.put("/{part_id}/", response_model=PartModel)
async def edit_part(part_id: str, data: PartUpdateModel, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    update_data = data.model_dump(exclude_unset=True)
    await _get_part(db, part_id)
    if "category" in update_data.keys():
        await _validate_category(db, update_data["category"])
    if "location" in update_data.keys() and not update_data["location"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Location field cannot be null.")
    try:
        updated_part = await update_part(db, part_id, update_data)
    except PartSerialNumberAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Part with this serial number already exists.")
    return updated_part


@router.delete("/{part_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_part(part_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    await _get_part(db, part_id)
    deleted = await delete_part(db, part_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Attempt to delete part with ID: {part_id} failed. Please try again later.")


@router.get("/search", response_model=PartListModel)
async def search_for_part(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    serial_number: str | None = None,
    name: str | None = "",
    description: str | None = "",
    category: str | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    room: str | None = None,
    bookcase: str | None = None,
    shelf: int | None = None,
    cuvette: int | None = None,
    column: int | None = None,
    row: int | None = None,
    ):
    filters = {
    "serial_number": {"serial_number": {"$eq": serial_number}},
    "name": {"name": {"$regex": name, "$options": "i"}},
    "description": {"description": {"$regex": description, "$options": "i"}},
    "category": {"category": {"$eq": category}},
    "min_quantity": {"quantity": {"$gte": min_quantity}},
    "max_quantity": {"quantity": {"$lte": max_quantity}},
    "min_price": {"price": {"$gte": min_price}},
    "max_price": {"price": {"$lte": max_price}},
    "room": {"room": {"$eq": room}},
    "bookcase": {"bookcase": {"$eq": bookcase}},
    "shelf": {"shelf": {"$eq": shelf}},
    "cuvette": {"cuvette": {"$eq": cuvette}},
    "column": {"column": {"$eq": column}},
    "row": {"row": {"$eq": row}},
    }
    query = {}
    for key in request.query_params.keys():
        filter = filters[key]
        if key not in ["min_quantity", "max_quantity", "min_price", "max_price"]:
            query.update(filter)
            continue
        for field_name, field_filter in filter.items():
            if field_name in query.keys():
                query[field_name].update(field_filter)
            else:
                query.update({field_name: field_filter})
    results = await read_parts(db, query)
    return PartListModel(parts=results)


async def _get_part(db: AsyncIOMotorDatabase, part_id: str) -> PartModel:
    try:
        part = await read_part(db, part_id)
    except InvalidPartIDError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid part ID provided.")
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Part with ID: {part_id} doesn't exist.")
    return part


async def _validate_category(db: AsyncIOMotorDatabase, category_name: str|None) -> None:
    if not category_name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category field cannot be null. The part must be assigned to category.")
    category = await read_category_by_name(db, category_name)
    if not category:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot assign part to non-existent category.")
    if category["parent_name"] == None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot assign part to base category.")
