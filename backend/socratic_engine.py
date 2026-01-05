# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
Concept-grounded Socratic followups driven by moduleXX_answers.json.

Returns:
  - str follow-up message, or
  - None if all required concepts are covered (so UI can advance)
"""
from typing import List
import re
import random
import streamlit as st
from concept_check import evaluate_concepts, is_uncertain, is_gibberish
from biochem_concepts import BIO_CONCEPTS

# ---------------------------------------------------------
# 🔍Smart semantic matching for key concepts
# ---------------------------------------------------------

def uncertainty_message(spec: dict) -> str:
    follow = (spec or {}).get(
        "uncertainty_followup",
        "Take a moment to jot down even a rough idea — what comes to mind?"
    ).strip()
    return (
        "That's totally okay — this concept can be tricky! 🧠💭\n"
        f"{follow}\n\n"
        "If you'd like, you can also click **Skip / Next Question ⏭️** to move on."
    )

def gibberish_message() -> str:
    return (
        "I couldn’t understand that response.\n"
        "Try again using a short sentence (a few real words), or click **Skip / Next Question ⏭️**."
    )

def socratic_followup(
    module_id: str,
    qid: int,                 # 0-based
    student_answer: str,      # combined text so far
    *,
    uncertain_now: bool = False,
    uncertain_count: int = 0,
    gibberish_now: bool = False,
    gibberish_count: int = 0,
):
    text = (student_answer or "").strip()

    # 1) Pull concept spec + missing concepts
    missing_required, _missing_optional, spec = evaluate_concepts(module_id, qid, text)

    # 2) ✅ Gibberish guardrail (ONLY based on latest submission)
    if gibberish_now:
        if gibberish_count >= 1:
            return (
                "Still not quite readable — let's keep moving.\n"
                "Click **Skip / Next Question ⏭️** when you're ready."
            )
        return gibberish_message()

    # 3) ✅ Uncertainty guardrail (ONLY based on latest submission)
    if uncertain_now:
        if uncertain_count >= 1:
            return (
                "That's totally okay — sometimes it's best to keep moving. "
                "If you'd like, click **Skip / Next Question ⏭️** when you're ready."
            )
        return uncertainty_message(spec)

    # 4) If no spec exists, fall back
    if not spec:
        return "Nice start — can you add one more molecular detail?"

    # 5) If all REQUIRED concepts covered → advance
    if not missing_required:
        return None

    # 6) Ask targeted followup
    concept = missing_required[0]
    encouragement_list = spec.get("encouragement", []) or []
    encouragement = random.choice(encouragement_list) if encouragement_list else "Keep going — you're on the right track."

    followups_map = spec.get("followups", {}) or {}
    follow_entry = followups_map.get(concept)

    if isinstance(follow_entry, list):
        follow_text = random.choice(follow_entry) if follow_entry else ""
    else:
        follow_text = follow_entry or ""

    if not follow_text:
        follow_text = "What part of the mechanism is still unclear?"

    return f"{encouragement} {follow_text}"
