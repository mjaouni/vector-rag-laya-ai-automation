"""Laya local, or explicitly labeled rules-only testing mode.

Laya probabilities are model estimates, not permissions to perform actions.
"""
from __future__ import annotations
from functools import lru_cache
import os
import re
from typing import Any
from .config import settings

HAZARDS = re.compile(r"\b(?:gas leak|smell of gas|carbon monoxide|smoke|fire|sparking|sparks|electrocution|burning smell|fumes)\b", re.I)
BOOKING = re.compile(r"\b(?:book|booking|schedule|appointment|technician|come tomorrow|send someone|visit)\b", re.I)
HUMAN = re.compile(r"\b(?:human|real person|supervisor|representative|call me|speak to someone)\b", re.I)

QUESTIONS = {
    "intent": {"type": "choice", "instructions": "What is this HVAC customer's primary request?", "criteria": {
        "booking": "Arrange a technician visit or appointment",
        "pricing": "Ask for price or cost",
        "maintenance": "Advice on routine servicing or maintenance",
        "information": "Ask about a service, area, or policy",
        "complaint": "Report dissatisfaction or complain",
        "other": "Other or ambiguous message"}},
    "hazard": {"type": "noul", "instructions": "Does the message indicate an immediate hazard such as gas, smoke, sparks, carbon monoxide or a fire?"},
    "human": {"type": "noul", "instructions": "Does the customer explicitly request a human agent?"},
}

@lru_cache(maxsize=1)
def laya_router():
    os.environ.setdefault("USE_TF", "0")
    from laya import Router
    return Router()


def classify(message: str) -> dict[str, Any]:
    if settings.decision_provider == "rules":
        # Diagnostic mode: no Laya inference; never label this output as Laya.
        intent = ("booking" if BOOKING.search(message) else "pricing" if re.search(r"\b(?:price|pricing|cost|how much)\b", message, re.I) else "maintenance" if re.search(r"\b(?:maintain|maintenance|service)\b", message, re.I) else "information")
        hazard = bool(HAZARDS.search(message)); human = bool(HUMAN.search(message))
        return {"provider":"rules-only", "intent":intent, "confidence":None, "hazard_probability":None, "human_probability":None,
                "hazard_flag":hazard, "booking_flag":bool(BOOKING.search(message)), "human_flag":human,
                "needs_review":hazard or human or bool(BOOKING.search(message))}
    if settings.decision_provider != "laya":
        raise ValueError("DECISION_PROVIDER must be laya or rules")
    result = laya_router().predict({"body": message}, QUESTIONS)
    answers = result.get("answers", {})
    choice = answers.get("intent", {})
    intent = choice.get("choice", "other")
    if intent not in QUESTIONS["intent"]["criteria"]:
        intent = "other"
    confidence = choice.get("confidence")
    if not isinstance(confidence, (float, int)):
        probabilities = choice.get("probabilities", {})
        if isinstance(probabilities, dict):
            confidence = probabilities.get(intent)
    hazard_p = answers.get("hazard", {}).get("noul")
    human_p = answers.get("human", {}).get("noul")
    hazard_flag = bool(HAZARDS.search(message)) or (isinstance(hazard_p, (int,float)) and hazard_p >= 0.50)
    human_flag = bool(HUMAN.search(message)) or (isinstance(human_p, (int,float)) and human_p >= 0.65)
    booking_flag = bool(BOOKING.search(message)) or intent == "booking"
    # Fail closed if scores needed for routing are unavailable.
    missing = not all(isinstance(score, (int, float)) and not isinstance(score, bool)
                      and 0 <= score <= 1 for score in (hazard_p, human_p, confidence))
    # Older Laya responses may omit confidence; do not silently manufacture one.
    unsure = intent == "other" or (isinstance(confidence, (int,float)) and confidence < 0.60)
    return {"provider": "laya-local", "intent": intent, "confidence": confidence, "hazard_probability":hazard_p,
            "human_probability":human_p, "hazard_flag": hazard_flag, "human_flag": human_flag, "booking_flag":booking_flag,
            "needs_review":hazard_flag or human_flag or booking_flag or missing or unsure,
            "routing_model": result.get("routing", {}).get("model", "unknown")}
