from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

config = dotenv_values(".env")

class DataBase:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

db = DataBase()

async def connect_db():
    db.client = AsyncIOMotorClient(config["ATLAS_URI"])
    db.database = db.client.get_database(config["DB_NAME"])

async def close_db():
    db.client.close()

async def get_db() -> AsyncIOMotorDatabase:
    return db.database