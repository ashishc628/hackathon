# db/mongo.py

from pymongo import MongoClient
from config import settings

# Use the Atlas SRV URI directly from env
# Example MONGO_URI:
# mongodb+srv://user:pass@ac-vpafuag.e07sxvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

client = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=30000,
    tls=True,                      # ensure TLS
    tlsAllowInvalidCertificates=True,  # <-- OK for hackathon/demo, not for production
)

db = client[settings.MONGO_DB_NAME]

requests_coll = db["requests"]
proofs_coll = db["proofResults"]
users_coll = db.get_collection("users")
