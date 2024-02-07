from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel
from routers.part import router as part_router
from routers.category import router as category_router
from dependencies import connect_db, close_db, get_db


async def create_collection_with_unique_index(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    fields: list[tuple[str, int]],
):
    collection = db[collection_name]
    index = IndexModel(fields, unique=True)
    await collection.create_indexes([index])
    # return collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.client = motor.motor_asyncio.AsyncIOMotorClient(config["ATLAS_URI"])
    await connect_db()
    app.db = await get_db()
    await create_collection_with_unique_index(app.db, "categories", [("name", ASCENDING)])
    await create_collection_with_unique_index(app.db, "parts", [("serial_number", ASCENDING)])

    yield

    await close_db()


app = FastAPI(lifespan=lifespan)


app.include_router(part_router)
app.include_router(category_router)


@app.get("/")
def root():
    return {"message": "Welcome! It's simple REST API for Parts Warehouse. Try it out at 127.0.0.1:8000/docs."}
