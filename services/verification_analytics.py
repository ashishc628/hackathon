# services/verification_analytics.py

from datetime import datetime, timedelta

from db.mongo import requests_coll, proofs_coll, DB_AVAILABLE



def _demo_mock_stats(intent: dict) -> dict:
    """
    Fallback stats when MongoDB is not available.
    Returns nice median-style numbers for the blood donation demo.
    """
    provider_name = intent.get("providerName") or "City Hospital Blood Drive"
    locality = intent.get("locality") or "L1"
    blood_type = intent.get("bloodType") or "B+"
    days = intent.get("timeWindowDays") or 1

    # Hard-coded but realistic demo numbers
    total_proofs = 50
    successful_proofs = 47
    success_rate = successful_proofs / total_proofs

    return {
        "providerName": provider_name,
        "useCase": intent.get("useCase") or "blood_donation",
        "locality": locality,
        "bloodType": blood_type,
        "timeWindowDays": days,
        "targetCount": 50,
        "totalProofs": total_proofs,
        "successfulProofs": successful_proofs,
        "successRate": success_rate,
        "requests": [
            {
                "requestId": "demo-request-1",
                "providerName": provider_name,
                "useCase": "blood_donation",
                "description": f"{blood_type} donors near {locality}",
                "attributeRequirements": {
                    "requiredBloodGroup": 5  # e.g. B+ encoding
                },
                "createdAt": datetime(2025, 11, 20).isoformat(),
                "expiresAt": (datetime(2025, 11, 20)
                              + timedelta(days=1)).isoformat(),
                "stats": {
                    "totalProofs": total_proofs,
                    "successfulProofs": successful_proofs,
                },
                "uniqueUserCount": 45,
            }
        ],
    }


def get_provider_campaign_stats(intent: dict) -> dict:
    """
    If MongoDB is available, query real collections.
    If not, return demo mock stats so the API always works.
    """
    # Fallback: no DB, use mock
    if not DB_AVAILABLE or requests_coll is None or proofs_coll is None:
        return _demo_mock_stats(intent)

    # --- Your existing real Mongo logic below (unchanged) ---
    # If you already have an aggregation pipeline, keep it.
    # Example skeleton:

    provider_name = intent.get("providerName")
    use_case = intent.get("useCase")
    time_window_days = intent.get("timeWindowDays", 7)

    now = datetime.utcnow()
    cutoff = now - timedelta(days=time_window_days)

    query = {}
    if provider_name:
        query["providerName"] = provider_name
    if use_case:
        query["useCase"] = use_case
    query["createdAt"] = {"$gte": cutoff}

    matching_requests = list(requests_coll.find(query))

    # Aggregate proofs for those requests
    request_ids = [r["requestId"] for r in matching_requests]
    proof_query = {"requestId": {"$in": request_ids}}

    proofs = list(proofs_coll.find(proof_query))

    total_proofs = len(proofs)
    successful_proofs = sum(1 for p in proofs if p.get("result") is True)
    success_rate = (successful_proofs / total_proofs) if total_proofs else 0.0

    # Attach per-request stats
    for r in matching_requests:
        rid = r["requestId"]
        r_proofs = [p for p in proofs if p["requestId"] == rid]
        r["stats"] = {
            "totalProofs": len(r_proofs),
            "successfulProofs": sum(1 for p in r_proofs if p.get("result") is True),
        }
        r["uniqueUserCount"] = len({p.get("userId") for p in r_proofs if p.get("userId")})

    return {
        "providerName": provider_name,
        "useCase": use_case,
        "timeWindowDays": time_window_days,
        "targetCount": 50,  # or pull from intent if you have it
        "requests": matching_requests,
        "totalProofs": total_proofs,
        "successfulProofs": successful_proofs,
        "successRate": success_rate,
    }
