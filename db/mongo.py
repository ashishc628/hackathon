# db/mongo.py

import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import settings

logger = logging.getLogger(__name__)

DB_AVAILABLE = False
client: Optional[MongoClient] = None
db = None
requests_coll = None
proofs_coll = None
users_coll = None

try:
    if settings.MONGO_URI:
        client = MongoClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,  # 5s
        )
        # Force a ping to check connectivity
        client.admin.command("ping")
        db = client[settings.MONGO_DB_NAME]
        requests_coll = db["requests"]
        proofs_coll = db["proofResults"]
        users_coll = db.get_collection("users")
        DB_AVAILABLE = True
        logger.info("Connected to MongoDB successfully.")
    else:
        logger.warning("MONGO_URI is empty; MongoDB disabled.")
except PyMongoError as e:
    logger.error(f"MongoDB connection failed: {e}")
    DB_AVAILABLE = False
    client = None
    db = None
    requests_coll = None
    proofs_coll = None
    users_coll = None
