from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.category import CategoryModel, CategoryCreateModel, CategoryUpdateModel, CategoryListModel
from crud.category import create_category, read_category, read_category_by_name, read_all_categories, update_category, delete_category, get_all_child_categories_names, has_parts_assigned, CategoryOrChildHasPartsAssignedError, CategoryNameAlreadyExistsError, InvalidCategoryIDError
from crud.part import update_parts_category_name
from dependencies import get_db


router = APIRouter(prefix="/category", tags=["category"])


@router.post("", response_model=CategoryModel, status_code=status.HTTP_201_CREATED)
async def add_category(category: CategoryCreateModel, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    if category.parent_name:
        await _validate_parent_category(db, category.parent_name)
    try:
        created_category = await create_category(db, category)
    except CategoryNameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category with this name already exists.")
    return created_category


@router.get("/{category_id}/", response_model=CategoryModel)
async def get_category(category_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    category = await _get_category(db, category_id)
    return category


@router.put("/{category_id}/", response_model=CategoryModel)
async def edit_category(category_id: str, data: CategoryUpdateModel, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    update_data = data.model_dump(exclude_unset=True)
    existing_category = await _get_category(db, category_id)
    if "parent_name" in update_data.keys():
        await _validate_new_parent_name(db, update_data["parent_name"], existing_category["name"])
    try:
        updated_category = await update_category(db, category_id, update_data)
    except CategoryNameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category with this name already exists.")
    if "name" in update_data.keys():
        await update_parts_category_name(db, existing_category["name"], update_data["name"])
    return updated_category

@router.delete("/{category_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(category_id: str, db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    category = await _get_category(db, category_id)
    try:
        deleted = await delete_category(db, category["name"])
    except CategoryOrChildHasPartsAssignedError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot delete this category, because it has parts assigned, or it has child categories with parts assigned.")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Attempt to delete category with ID: {category_id} failed. Please try again later.")


@router.get("", response_model=CategoryListModel)
async def get_all_categories(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    categories = await read_all_categories(db)
    return CategoryListModel(categories=categories)


async def _get_category(db: AsyncIOMotorDatabase, category_id: str) -> CategoryModel:
    try:
        category = await read_category(db, category_id)
    except InvalidCategoryIDError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category ID provided.")
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with ID: {category_id} doesn't exist.")
    return category


async def _validate_parent_category(db: AsyncIOMotorDatabase, parent_category_name: str) -> None:
    parent_category = await read_category_by_name(db, parent_category_name)
    if not parent_category:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Parent category named '{parent_category_name}' doesn't exist.")


async def _validate_new_parent_name(db: AsyncIOMotorDatabase, new_parent_name: str|None, current_category_name: str) -> None:
    if not new_parent_name:
        category_has_part_assigned = await has_parts_assigned(db, current_category_name)
        if category_has_part_assigned:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot make base category from category that has parts assigned.")
        return
    await _validate_parent_category(db, new_parent_name)
    if new_parent_name == current_category_name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category's name and parent_name cannot be equal - category cannot be its parent category.")
    child_categories = await get_all_child_categories_names(db, current_category_name)
    if new_parent_name in child_categories:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category cannot become subcategory of its own subcategory.")
