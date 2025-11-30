# app/services/verification_analytics.py


from datetime import datetime, timedelta
from typing import Dict, Any

from app.db.mongo import requests_coll, proofs_coll


def get_provider_campaign_stats(intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate zk-loci verification stats for one provider/useCase/time window.

    intent keys:
      - providerName: optional string
      - useCase: optional string
      - timeWindowDays: optional int (default 1)
      - targetCount: optional int (default 25)
    """
    provider_name = intent.get("providerName")
    use_case = intent.get("useCase")
    time_window_days = intent.get("timeWindowDays") or 1   # default 1 day
    target_count = intent.get("targetCount") or 25         # default target 25

    now = datetime.utcnow()
    since = now - timedelta(days=time_window_days)

    # 1) Find matching active requests
    query: Dict[str, Any] = {
        "status": "active",
        "createdAt": {"$gte": since},
    }
    if provider_name:
        query["providerName"] = provider_name
    if use_case:
        query["useCase"] = use_case

    matching_requests = list(
        requests_coll.find(
            query,
            {
                "_id": 0,
                "requestId": 1,
                "providerName": 1,
                "useCase": 1,
                "description": 1,
                "stats": 1,
                "attributeRequirements": 1,
                "expiresAt": 1,
                "createdAt": 1,
            },
        )
    )

    if not matching_requests:
        return {
            "providerName": provider_name,
            "useCase": use_case,
            "timeWindowDays": time_window_days,
            "targetCount": target_count,
            "requests": [],
            "totalProofs": 0,
            "successfulProofs": 0,
            "successRate": 0.0,
        }

    request_ids = [r["requestId"] for r in matching_requests]

    # 2) Aggregate proofs for those requests
    pipeline = [
        {
            "$match": {
                "requestId": {"$in": request_ids},
                "createdAt": {"$gte": since},
            }
        },
        {
            "$group": {
                "_id": "$requestId",
                "totalProofs": {"$sum": 1},
                "successfulProofs": {
                    "$sum": {
                        "$cond": [{"$eq": ["$result", True]}, 1, 0]
                    }
                },
                "uniqueUsers": {"$addToSet": "$userId"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "requestId": "$_id",  # important: map _id → requestId
                "totalProofs": 1,
                "successfulProofs": 1,
                "uniqueUserCount": {"$size": "$uniqueUsers"},
            }
        },
    ]

    agg_results = list(proofs_coll.aggregate(pipeline))
    stats_by_request = {a["requestId"]: a for a in agg_results}

    total_proofs = 0
    successful_proofs = 0

    enriched_requests = []
    for req in matching_requests:
        rid = req["requestId"]
        agg = stats_by_request.get(
            rid,
            {
                "totalProofs": 0,
                "successfulProofs": 0,
                "uniqueUserCount": 0,
            },
        )
        total_proofs += agg["totalProofs"]
        successful_proofs += agg["successfulProofs"]

        enriched_requests.append(
            {
                **req,
                "totalProofs": agg["totalProofs"],
                "successfulProofs": agg["successfulProofs"],
                "uniqueUserCount": agg["uniqueUserCount"],
            }
        )

    success_rate = (
        successful_proofs / total_proofs if total_proofs > 0 else 0.0
    )

    return {
        "providerName": provider_name,
        "useCase": use_case,
        "timeWindowDays": time_window_days,
        "targetCount": target_count,
        "requests": enriched_requests,
        "totalProofs": total_proofs,
        "successfulProofs": successful_proofs,
        "successRate": round(success_rate, 3),
    }
