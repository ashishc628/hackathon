# scripts/seed_zkloci.py
import os
from datetime import datetime, timedelta
import random
import uuid

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "zk_loci")

def seed():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    requests_coll = db["requests"]
    proofs_coll = db["proofResults"]
    users_coll = db["users"]

    # Clean existing
    requests_coll.drop()
    proofs_coll.drop()
    users_coll.drop()

    now = datetime.utcnow()

    # --- Example: one blood donation request from City Hospital ---
    request_id_1 = str(uuid.uuid4())
    request_doc_1 = {
        "requestId": request_id_1,
        "providerId": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "providerName": "City Hospital Blood Drive",
        "type": "bloodGroup",
        "useCase": "blood_donation",
        "locationRequirements": None,
        "attributeRequirements": {
            "requiredBloodGroup": 1  # O+
        },
        "description": "O+ donors needed for emergency surgery",
        "requestedData": ["blood_group"],
        "status": "active",
        "expiresAt": now + timedelta(days=1),
        "createdAt": now - timedelta(hours=2),
        "updatedAt": now - timedelta(hours=1),
        "stats": {
            "totalProofs": 0,          # will update with real counts below
            "successfulProofs": 0,
        },
    }

    # Another request (for variety)
    request_id_2 = str(uuid.uuid4())
    request_doc_2 = {
        "requestId": request_id_2,
        "providerId": "0xCOMPANY123456",
        "providerName": "Metro Office Attendance",
        "type": "location",
        "useCase": "workplace_attendance",
        "locationRequirements": {
            "centerLat": 37.7749,
            "centerLon": -122.4194,
            "radius": 500,
            "maxDuration": 3600,
        },
        "attributeRequirements": None,
        "description": "On-site presence verification for staff",
        "requestedData": ["location_proof"],
        "status": "active",
        "expiresAt": now + timedelta(days=7),
        "createdAt": now - timedelta(days=1),
        "updatedAt": now - timedelta(hours=3),
        "stats": {
            "totalProofs": 0,
            "successfulProofs": 0,
        },
    }

    requests_coll.insert_many([request_doc_1, request_doc_2])

    # --- Seed some proofResults for request 1 (blood donation) ---
    proof_docs = []
    user_ids = [
        "0xUSER1",
        "0xUSER2",
        "0xUSER3",
        "0xUSER4",
        "0xUSER5",
    ]

    for u in user_ids:
        success = random.random() < 0.8  # ~80% success
        proof_docs.append({
            "proofId": str(uuid.uuid4()),
            "requestId": request_id_1,
            "userId": u,
            "proofType": "bloodGroup",
            "ipfsCID": f"Qm{uuid.uuid4().hex[:20]}",
            "ipfsUrl": "https://gateway.mypinata.cloud/ipfs/" + f"Qm{uuid.uuid4().hex[:20]}",
            "result": success,
            "provider": "City Hospital Blood Drive",
            "providerAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "metadata": {
                "requiredBloodGroup": 1,
            },
            "timestamp": int((now - timedelta(minutes=random.randint(0, 120))).timestamp() * 1000),
            "createdAt": now - timedelta(minutes=random.randint(0, 120)),
            "updatedAt": now - timedelta(minutes=random.randint(0, 60)),
            "status": "verified" if success else "failed",
            "transactionHash": None,
            "blockNumber": None,
            "tags": ["bloodGroup", "City Hospital", f"user:{u}"],
        })

    # --- Some proofs for request 2 (location) ---
    office_users = ["0xEMP1", "0xEMP2", "0xEMP3"]
    for u in office_users:
        success = random.random() < 0.7
        proof_docs.append({
            "proofId": str(uuid.uuid4()),
            "requestId": request_id_2,
            "userId": u,
            "proofType": "location",
            "ipfsCID": f"Qm{uuid.uuid4().hex[:20]}",
            "ipfsUrl": "https://gateway.mypinata.cloud/ipfs/" + f"Qm{uuid.uuid4().hex[:20]}",
            "result": success,
            "provider": "Metro Office Attendance",
            "providerAddress": "0xCOMPANY123456",
            "metadata": {
                "sessionDuration": random.randint(300, 3600),
            },
            "timestamp": int((now - timedelta(minutes=random.randint(0, 1440))).timestamp() * 1000),
            "createdAt": now - timedelta(minutes=random.randint(0, 1440)),
            "updatedAt": now - timedelta(minutes=random.randint(0, 60)),
            "status": "verified" if success else "failed",
            "transactionHash": None,
            "blockNumber": None,
            "tags": ["location", "Metro Office", f"user:{u}"],
        })

    proofs_coll.insert_many(proof_docs)

    # --- Update stats in requests collection based on seeded proofs ---
    for r in [request_doc_1, request_doc_2]:
        rid = r["requestId"]
        total = proofs_coll.count_documents({"requestId": rid})
        successful = proofs_coll.count_documents({"requestId": rid, "result": True})
        requests_coll.update_one(
            {"requestId": rid},
            {"$set": {"stats.totalProofs": total, "stats.successfulProofs": successful}}
        )

    # --- Seed users collection (aggregated user stats) ---
    # simple example for one user
    users_coll.insert_one({
        "userId": "0xUSER1",
        "stats": {
            "totalProofs": 5,
            "successfulProofs": 4,
            "proofsByType": {
                "location": 1,
                "age": 0,
                "bloodGroup": 3,
                "cibilScore": 1,
            },
        },
        "createdAt": now - timedelta(days=10),
        "updatedAt": now,
        "lastActive": now,
    })

    print("Seeded zk-loci mock data successfully.")

if __name__ == "__main__":
    seed()
