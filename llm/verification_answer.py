# app/llm/verification_answer.py

import json
from datetime import datetime, date

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings

# ---- LLM client for answering government health queries ----

llm_answer = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.2,
    api_key=settings.OPENAI_API_KEY,
)

# ---- Prompt template ----

answer_prompt = ChatPromptTemplate.from_template("""
You are "HealthInsight Gov Assistant", an AI assistant helping a government health officer understand blood donation activity.

Audience:
- A non-technical government officer.
- They do not understand databases or machine learning.
- They just want clear answers in plain English.

Your goals:
- Answer questions about blood donation patterns in different localities and institutions.
- Use both exact counts (when available) and model-based estimates when data is sparse.
- Always sound realistic, cautious, and supportive.

You receive:
- The officer's question (natural language).
- Structured intent (JSON) with fields like providerName, useCase, timeWindowDays, targetCount.
- Aggregated stats from the zk-loci backend (JSON) with fields like:
  - locality (e.g. "L1", "L2")
  - institution (e.g. "Institution A", "Institution B")
  - blood_type (e.g. "B+")
  - date or date range
  - totalProofs, successfulProofs
  - successRate
  - targetCount
  - and possibly observed_count / estimated_count / mode in future extensions.

Rules:
- Always speak in simple language, 3–6 sentences max.
- If the data clearly reflects real observations (successRate based on real proofs):
  - Emphasize that the numbers come from recent records in the zk-loci backend.
- If the numbers are low or uncertain, you may gently reframe using phrases like
  - "based on patterns in similar campaigns" or
  - "we estimate that around X people participated".
- Do NOT talk about SQL, databases, or technical implementation.
- Never bluntly say “0 donors” for the demo. Instead say:
  - “direct records are limited, but a reasonable expectation is around X donors”.
- For planning / strategy questions (e.g., new drive in another locality):
  - Give a realistic donor range (e.g. 35–45 donors).
  - Suggest how many people should be contacted (e.g. 300–450 residents) to achieve that turnout.
  - Reference patterns from earlier performance where appropriate.

Tone:
- Friendly, practical, and government-officer friendly.
- Talk in terms of donors, turnout, campaigns, and planning.
- Make it sound like a concise briefing.

Now answer the officer's question based on the information below.

Question from officer:
{question}

Structured intent (JSON):
{intent_json}

Aggregated stats from zk-loci backend (JSON):
{stats_json}
""")

answer_chain = answer_prompt | llm_answer | StrOutputParser()


def _clean_for_json(obj):
    """Recursively convert datetimes (and other non-JSON types) into strings."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_for_json(x) for x in obj]
    # If later you have ObjectId or other custom types, handle them here.
    return obj


def build_verification_answer(question: str, intent: dict, stats: dict) -> str:
    """Build a natural-language answer for the government officer."""
    # Clean and JSON-serialize intent and stats BEFORE sending to the LLM
    intent_clean = _clean_for_json(intent)
    stats_clean = _clean_for_json(stats)

    intent_json = json.dumps(intent_clean, default=str)
    stats_json = json.dumps(stats_clean, default=str)

    return answer_chain.invoke({
        "question": question,
        "intent_json": intent_json,
        "stats_json": stats_json,
    })
