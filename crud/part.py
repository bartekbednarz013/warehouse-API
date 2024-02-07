from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.part import PartModel, PartCreateModel, PartUpdateModel, PartListModel


class PartSerialNumberAlreadyExistsError(Exception):
    pass


class InvalidPartIDError(Exception):
    pass


async def create_part(db: AsyncIOMotorDatabase, part: PartCreateModel) -> PartModel:
    try:
        new_part = await db.parts.insert_one(part.model_dump())
        created_part = await db.parts.find_one({"_id": new_part.inserted_id})
        return created_part
    except DuplicateKeyError:
        raise PartSerialNumberAlreadyExistsError()


async def read_part(db: AsyncIOMotorDatabase, part_id: str) -> PartModel:
    try:
        part = await db.parts.find_one({"_id": ObjectId(part_id)})
        return part
    except InvalidId:
        raise InvalidPartIDError()


async def update_part(db: AsyncIOMotorDatabase, part_id: str, part: PartUpdateModel) -> PartModel:
    try:
        await db.parts.find_one_and_update({"_id": ObjectId(part_id)}, {"$set": part})
        updated_part = await db.parts.find_one({"_id": ObjectId(part_id)})
        return updated_part
    except DuplicateKeyError:
        raise PartSerialNumberAlreadyExistsError()


async def delete_part(db: AsyncIOMotorDatabase, part_id: str) -> bool:
    deleted_part = await db.parts.delete_one({"_id": ObjectId(part_id)})
    return deleted_part.deleted_count == 1


async def read_parts(db: AsyncIOMotorDatabase, query: dict | None = None) -> PartListModel:
    parts = await db.parts.find(query).to_list(length=None)
    return parts


async def update_parts_category_name(db: AsyncIOMotorDatabase, current_category_name: str, new_category_name: str) -> None:
    await db.parts.find_one_and_update({"category": current_category_name}, {"$set": {"category": new_category_name}})
