# # app/llm/router.py
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from app.config import settings
#
# llm_router = ChatOpenAI(
#     model=settings.OPENAI_MODEL,
#     temperature=0.0,
#     api_key=settings.OPENAI_API_KEY,
# )
#
# router_prompt = ChatPromptTemplate.from_template("""
# You are a router for zk-loci queries.
#
# If the question is about:
# - verification requests, proofs, proof results, IPFS, Pinata, zk proofs, stats, providers, success rate, failure rate, user reputation, or the zk-loci system itself → "verification_analytics"
# Otherwise → "generic"
#
# Return ONLY:
# verification_analytics
# generic
#
# User question:
# {question}
# """)
#
# router_chain = router_prompt | llm_router | StrOutputParser()
#
# def route_question(question: str) -> str:
#     label = router_chain.invoke({"question": question}).strip().lower()
#     if label not in {"verification_analytics", "generic"}:
#         return "generic"
#     return label
# app/llm/router.py

def route_question(question: str) -> str:
    """
    Very simple rule-based router for the demo.

    If the question looks like it's about donors, blood donation,
    localities, institutions, campaigns, or turnout,
    route it to 'verification_analytics'.

    Otherwise, route it to 'generic'.
    """
    q = (question or "").lower()

    blood_keywords = [
        "blood", "donor", "donors", "b+", "o+", "o-", "ab+", "ab-",
        "donation drive", "donation campaign"
    ]
    gov_campaign_keywords = [
        "locality", "l1", "l2", "institution a", "institution b",
        "turnout", "campaign", "participation", "drive", "target",
        "how many people", "how many donors"
    ]

    if any(k in q for k in blood_keywords + gov_campaign_keywords):
        return "verification_analytics"

    # fallback
    return "generic"
