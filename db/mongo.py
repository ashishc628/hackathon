# app/db/mongo.py
from pymongo import MongoClient
from app.config import settings


client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

requests_coll = db["requests"]
proofs_coll = db["proofResults"]
users_coll = db["users"]
