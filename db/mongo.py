# db/mongo.py

from pymongo import MongoClient
from config import settings

client = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=30000  # 30s
)

db = client[settings.MONGO_DB_NAME]

requests_coll = db["requests"]
proofs_coll = db["proofResults"]
users_coll = db.get_collection("users")
