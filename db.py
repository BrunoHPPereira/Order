# db.py
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION, MONGO_COLLECTION_REVIEW

# Criação única e persistente da conexao MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def get_db_collection():
    return db[MONGO_COLLECTION]

def get_db_collection_review():
    return db[MONGO_COLLECTION_REVIEW]
