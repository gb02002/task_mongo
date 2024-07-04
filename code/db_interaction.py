import asyncio, logging, os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import ASCENDING
import pymongo.errors

load_dotenv(dotenv_path="../.env")

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

mongo_host = os.getenv("MONGO_HOST")
mongo_port = os.getenv("MONGO_PORT")
mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_db = os.getenv("MONGO_DB")
mongo_collection = os.getenv("MONGO_COLLECTION")

# Формирование полной строки подключения
if mongo_user and mongo_password:
    DATABASE_URL = (
        f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
    )
else:
    DATABASE_URL = f"mongodb://{mongo_host}:{mongo_port}/"

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[mongo_db]
collection = db[mongo_collection]


async def execute_request_db(data: tuple) -> list | tuple[Exception, str]:
    """Сам запрос. Использует тело из коллекции pipelines ниже"""
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            logger.debug("We are in execute request db")
            date_from, date_upto, request_type = data
            pipeline = pipelines[request_type](date_from, date_upto)

            logger.debug(f"pipeline {pipeline}")

            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)

            logger.debug(f"Сделан запрос {request_type, result}")

            return result
        except pymongo.errors.OperationFailure as e:
            logger.error(f"Operation failed: {e}")
            return e, f"Operation failed: {e}"
        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"Connection failed: {e}")
            retry_count += 1
            await asyncio.sleep(2)
        except Exception as e:
            return e, f"Unexpected error: {e}"


#  Варианты и шаблоны запросов
pipelines = {
    "hour": lambda dt_from, dt_upto: [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dt"},
                    "month": {"$month": "$dt"},
                    "day": {"$dayOfMonth": "$dt"},
                    "hour": {"$hour": "$dt"},
                },
                "total_value": {"$sum": "$value"},
            }
        },
        {"$sort": {"_id": ASCENDING}},
    ],
    "day": lambda dt_from, dt_upto: [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dt"},
                    "month": {"$month": "$dt"},
                    "day": {"$dayOfMonth": "$dt"},
                },
                "total_value": {"$sum": "$value"},
            }
        },
        {"$sort": {"_id": ASCENDING}},
    ],
    "week": lambda dt_from, dt_upto: [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dt"},
                    "week": {"$isoWeek": "$dt"},  # Use $isoWeek if preferred
                },
                "total_value": {"$sum": "$value"},
            }
        },
        {"$sort": {"_id": ASCENDING}},
    ],
    "month": lambda dt_from, dt_upto: [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dt"},
                    "month": {"$month": "$dt"},
                },
                "total_value": {"$sum": "$value"},
            }
        },
        {"$sort": {"_id": ASCENDING}},
    ],
}
