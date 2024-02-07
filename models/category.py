from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.part import PyObjectId


class CategoryModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    parent_name: str | None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        )


class CategoryCreateModel(BaseModel):
    name: str
    parent_name: str | None = None

    @model_validator(mode="after")
    def verify_names(cls, values):
        if values.name and values.name == values.parent_name:
            raise ValueError("Category's name and parent_name cannot be equal - category cannot be its parent category.")
        return values


class CategoryUpdateModel(CategoryCreateModel):
    name: str | None = None


class CategoryListModel(BaseModel):
    categories: list[CategoryModel]