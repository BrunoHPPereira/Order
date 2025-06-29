from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def get_db_collection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]
