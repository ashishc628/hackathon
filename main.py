# app/main.py
# from fastapi import FastAPI
# from app.models.api import QueryRequest, QueryResponse
# from app.llm.router import route_question
# from app.llm.verification_intent import extract_verification_intent
# from app.llm.verification_answer import build_verification_answer
# from app.services.verification_analytics import get_provider_campaign_stats



# from fastapi import FastAPI
# from app.models.api import QueryRequest, QueryResponse
# from app.llm.router import route_question
# from app.llm.verification_intent import extract_verification_intent
# from app.llm.verification_answer import build_verification_answer
# from app.services.verification_analytics import get_provider_campaign_stats

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.api import QueryRequest, QueryResponse
from llm.router import route_question
from llm.verification_intent import extract_verification_intent
from llm.verification_answer import build_verification_answer
from services.verification_analytics import get_provider_campaign_stats


app = FastAPI(title="zk-loci Analytics API")

@app.get("/")
def root():
    return {"message": "zk-loci Analytics API is running"}

@app.post("/analytics/query", response_model=QueryResponse)
def analytics_query(payload: QueryRequest):
    question = payload.question
    route = route_question(question)

    if route == "verification_analytics":
        intent = extract_verification_intent(question)
        stats = get_provider_campaign_stats(intent)
        answer = build_verification_answer(question, intent, stats)
        return QueryResponse(answer=answer, route=route, raw_stats=stats)

    # generic fallback (simple echo for now)
    return QueryResponse(
        answer="This question is not recognized as a zk-loci analytics query. Please ask about verification stats, proofs, providers, or use cases.",
        route="generic",
        raw_stats=None,
    )
