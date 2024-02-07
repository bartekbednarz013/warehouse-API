from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class Location(BaseModel):
    room: str
    bookcase: str
    shelf: int
    cuvette: int
    column: int
    row: int


class PartCreateModel(BaseModel):
    serial_number: str
    name: str
    description: str
    category: str
    quantity: int
    price: float
    location: Location


class PartModel(PartCreateModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        )


class PartUpdateModel(BaseModel):
    serial_number: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    quantity: int | None = None
    price: float | None = None
    location: Location | None = None


class PartListModel(BaseModel):
    parts: list[PartModel]
