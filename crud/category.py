from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from models.category import CategoryModel, CategoryCreateModel, CategoryUpdateModel, CategoryListModel


class CategoryOrChildHasPartsAssignedError(Exception):
    pass


class CategoryNameAlreadyExistsError(Exception):
    pass


class InvalidCategoryIDError(Exception):
    pass


async def create_category(db: AsyncIOMotorDatabase, category: CategoryCreateModel) -> CategoryModel:
    try:
        new_category = await db.categories.insert_one(category.model_dump())
        created_category = await db.categories.find_one({"_id": new_category.inserted_id})
        return created_category
    except DuplicateKeyError:
        raise CategoryNameAlreadyExistsError()


async def read_category(db: AsyncIOMotorDatabase, category_id: str) -> CategoryModel:
    try:
        category = await db.categories.find_one({"_id": ObjectId(category_id)})
        return category
    except InvalidId:
        raise InvalidCategoryIDError()


async def read_category_by_name(db: AsyncIOMotorDatabase, category_name: str) -> CategoryModel:
    category = await db.categories.find_one({"name": category_name})
    return category


async def read_all_categories(db: AsyncIOMotorDatabase) -> CategoryListModel:
    categories = await db.categories.find().to_list(length=None)
    return categories


async def update_category(db: AsyncIOMotorDatabase, category_id: str, category: CategoryUpdateModel) -> CategoryModel:
    try:
        await db.categories.find_one_and_update({"_id": ObjectId(category_id)}, {"$set": category})
        updated_category = await db.categories.find_one({"_id": ObjectId(category_id)})
        return updated_category
    except DuplicateKeyError:
        raise CategoryNameAlreadyExistsError()


async def delete_category(db: AsyncIOMotorDatabase, category_name: str) -> bool:
    child_categories = await get_all_child_categories_names(db, category_name)
    categories = [category_name]
    categories.extend(child_categories)
    categories_with_parts = await db.parts.find({"category": {"$in": categories}}).to_list(length=None)
    if categories_with_parts:
        raise CategoryOrChildHasPartsAssignedError()
    deleted_categories = await db.categories.delete_many({"name": {"$in": categories}})
    return deleted_categories.deleted_count != 0


async def is_base_category(db: AsyncIOMotorDatabase, category_name: str) -> bool:
    category = await read_category_by_name(db, category_name)
    if category["parent_name"] == None:
        return True
    return False


async def get_all_child_categories_names(db: AsyncIOMotorDatabase, category_name: str) -> list[str]:
    all_children = []
    children_categories = db.categories.find({"parent_name": category_name})
    for child_category in await children_categories.to_list(length=None):
        child_category_name = child_category["name"]
        all_children.append(child_category_name)
        all_children += await get_all_child_categories_names(db, child_category_name)
    return all_children


async def has_parts_assigned(db: AsyncIOMotorDatabase, category_name: str) -> bool:
    parts = await db.parts.find({"category": {"$eq": category_name}}).to_list(length=None)
    if parts:
        return True
    return False