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
from concept_check import evaluate_concepts  # <-- uses BIO_CONCEPTS & JSON
from biochem_concepts import BIO_CONCEPTS
from concept_check import is_uncertain
import streamlit as st

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

def socratic_followup(module_id: str, qid: int, student_answer: str):
    """
    module_id: "module01"
    qid: 0-based question index from pointer (0,1,2,...)
    student_answer: combined text so far for this question

    Uses module answers JSON to decide next follow-up.
    """
    text = (student_answer or "").strip()

    # IMPORTANT: your JSON keys are "1", "2", ... but qid is 0-based
    qnum = qid + 1

    # Always load spec so uncertainty can be question-specific
    missing_required, missing_optional, spec = evaluate_concepts(module_id, qnum, text)

    # ---------- Uncertainty handling (only once per question) ----------
    if is_uncertain(text):
        key = (module_id, qnum)

        if "uncertain_seen" not in st.session_state:
            st.session_state.uncertain_seen = set()

        if key in st.session_state.uncertain_seen:
            # second uncertainty → encourage skip only
            return (
                "That's okay — sometimes it's best to keep moving.\n"
                "You can click **Skip / Next Question ⏭️** when you're ready."
            )

        # first uncertainty → question-specific uncertainty followup
        st.session_state.uncertain_seen.add(key)
        return uncertainty_message(spec)

    # If no spec exists for this question, fall back to generic
    if not spec:
        return "Nice start — can you add one more molecular detail?"

    # If all REQUIRED concepts are covered → UI should move on
    if not missing_required:
        return None

    # Focus follow-up on the first missing required concept
    concept = missing_required[0]

    encouragement_list = spec.get("encouragement", []) or []
    encouragement = (
        random.choice(encouragement_list)
        if encouragement_list
        else "Keep going — you're on the right track."
    )

    followup_map = spec.get("followups", {}) or {}
    follow_entry = followup_map.get(concept)

    if isinstance(follow_entry, list):
        follow_text = random.choice(follow_entry) if follow_entry else ""
    else:
        follow_text = follow_entry or ""

    if not follow_text:
        follow_text = "What part of the mechanism is still unclear?"

    return f"{encouragement} {follow_text}"