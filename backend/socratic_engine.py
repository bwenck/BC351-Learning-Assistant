# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""
from typing import List
import re
import random
from concept_check import evaluate_concepts  # <-- uses BIO_CONCEPTS & JSON
from biochem_concepts import BIO_CONCEPTS
from concept_check import is_uncertain

# ---------------------------------------------------------
# 🔍Smart semantic matching for key concepts
# ---------------------------------------------------------

def socratic_followup(module_id: str, qid: int, student_answer: str):
    """
    Decide what to ask next for (module_id, question qid) given the student's
    combined answer text for that question.

    Returns:
      - a single follow-up string, OR
      - None if all required concepts are covered (so the UI knows to advance)
    """
    # normalize first
    text = (student_answer or "").strip()

    # 🚨 never auto-advance on uncertainty
    if is_uncertain(text):
        return {
            "type": "uncertain",
            "message": (
                "That's totally okay — this concept can be tricky! 🧠💭\n"
                "Take a moment to think it through, or feel free to click "
                "**Skip / Next Question ⏭️** if you'd like to move on."
            )
        }

    if not text:
        return "Take a moment to jot down even a rough idea — what comes to mind first for this question?"

    # 🔍 Ask concept_check to evaluate required/optional concepts
    missing_required, missing_optional, spec = evaluate_concepts(
        module_id,
        qid,
        text,
    )

    # If we don't have a spec for this question, fall back to a generic nudge
    if not spec:
        return "Nice start — can you add a bit more detail about the key idea here?"

    # ✅ If *no required concepts* are missing → all core ideas are present → move on
    if not missing_required:
        return None

    # Pick the *first* missing required concept to focus the follow-up
    concept = missing_required[0]

    # Encouragement message
    encouragement_list = spec.get("encouragement", [])
    encouragement = random.choice(encouragement_list) if encouragement_list else "Good thinking — let's sharpen this a bit."

    # Concept-specific follow-up(s)
    followup_map = spec.get("followups", {})
    followup_entry = followup_map.get(concept)

    if isinstance(followup_entry, list):
        follow_text = random.choice(followup_entry) if followup_entry else ""
    else:
        # allow simple string as well
        follow_text = followup_entry or ""

    if not follow_text:
        # Fallback if no specific followup is defined
        follow_text = "Can you say a bit more about this idea in molecular terms?"

    return f"{encouragement} {follow_text}"