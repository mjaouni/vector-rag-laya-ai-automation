from __future__ import annotations
from uuid import uuid4
from .decisions import classify
from .retrieval import retrieve
from .generation import generate


def process_question(message: str, request_id: str | None = None) -> dict:
    request_id = request_id or str(uuid4())
    # Fail closed if Laya fails or is not installed; don't claim this is a model decision.
    try:
        decision = classify(message)
    except Exception as exc:
        return {"request_id":request_id, "status":"needs_review", "decision":{"provider":"unavailable", "needs_review":True},
                "answer":"The decision model is unavailable. This request needs a human review.",
                "sources":[], "retrieved":[], "reason":f"Decision model unavailable ({type(exc).__name__}); inspect API logs"}
    if decision["hazard_flag"]:
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"This may describe a safety hazard. Contact appropriate local emergency services or a qualified professional. No appointment has been made.",
                "sources":[], "retrieved":[], "reason":"potential_hazard"}
    try:
        hits = retrieve(message)
    except Exception as exc:
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"Knowledge retrieval is unavailable. An employee should review this request.",
                "sources":[], "retrieved":[], "reason":f"retrieval_unavailable:{type(exc).__name__}"}
    if not hits:
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"I don't have enough verified information in the sample documents to answer that.",
                "sources":[], "retrieved":[], "reason":"insufficient_evidence"}
    if decision["booking_flag"] or decision["human_flag"]:
        # Provide source information, but don't call generation or pretend to book.
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"I've identified your request for an appointment or human assistance. No booking has been made; a person should review it.",
                "sources":sorted({h["source"] for h in hits}), "retrieved":hits,
                "reason":"human_or_booking_request"}
    if decision["needs_review"]:
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"This question requires human review because the classifier was uncertain.",
                "sources":sorted({h["source"] for h in hits}), "retrieved":hits, "reason":"uncertain_classification"}
    try:
        answer = generate(message, hits)
    except Exception as exc:
        return {"request_id":request_id, "status":"needs_review", "decision":decision,
                "answer":"The answer generator is unavailable; please ask an employee.",
                "sources":sorted({h["source"] for h in hits}), "retrieved":hits,
                "reason":f"generation_unavailable:{type(exc).__name__}"}
    return {"request_id":request_id, "status":"answered", "decision":decision, "answer":answer,
            "sources":sorted({h["source"] for h in hits}), "retrieved":hits, "reason":"grounded_response"}
