# app/llm/verification_intent.py
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings

llm_intent = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.0,
    api_key=settings.OPENAI_API_KEY,
)

intent_prompt = ChatPromptTemplate.from_template("""
You extract structured info from questions about zk-loci verification analytics.

Return ONLY valid JSON with these keys:
- "providerName" (string or null)
- "useCase" (string or null)
- "timeWindowDays" (int or null)
- "targetCount" (int or null)

If something is not mentioned, use null. Do not add extra keys.

Question:
{question}
""")

intent_chain = intent_prompt | llm_intent | StrOutputParser()

def extract_verification_intent(question: str) -> dict:
    raw = intent_chain.invoke({"question": question})
    try:
        data = json.loads(raw)
    except Exception:
        data = {}
    # Provide safe defaults
    return {
        "providerName": data.get("providerName"),
        "useCase": data.get("useCase"),
        "timeWindowDays": data.get("timeWindowDays"),
        "targetCount": data.get("targetCount"),
    }
