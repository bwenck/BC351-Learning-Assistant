# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""
from typing import List
import re
from backend.question_loader import load_concept_keys

# ---------------------------------------------------------
# 🔍Smart semantic matching for key concepts
# ---------------------------------------------------------
import re

def concept_covered(concept: str, student_answer: str) -> bool:
    """
    Returns True if the student's answer semantically matches the concept.
    Uses loose stem matching with a threshold instead of strict exact matching.
    """
    student = student_answer.lower()
    concept = concept.lower()

    # Extract words and build stems (mutat, prolife, regula, tumor, monoc, colon, etc.)
    words = [w for w in re.findall(r"[a-zA-Z]+", concept) if len(w) > 3]
    stems = [w[:5] for w in words]  # take first 5 letters as a crude stem

    if not stems:
        return False

    # Count how many stems appear in the student's answer
    hits = sum(1 for stem in stems if stem in student)

    # Require at least half the stems (or minimum 2) to call it "covered"
    needed = max(2, len(stems) // 2)

    return hits >= needed

def socratic_followup(module_id: str, q_index: int, student_answer: str) -> str:
    """
    Pick a single Socratic follow-up based on which key concepts are still missing.
    Uses key_concepts and followups from <module_id>_answers.json.
    """
    spec = load_concept_keys(module_id).get(str(q_index + 1), {})
    key_concepts = spec.get("key_concepts", [])
    followups    = spec.get("followups", [])
    encouragement = spec.get("encouragement", [])

    text = (student_answer or "").strip()
    if not text:
        return "Take a moment to jot down even a rough idea — what comes to mind first for this question?"

    lower = text.lower()

    # 🔹 Handle “I don’t know / not sure”
    if any(phrase in lower for phrase in ["i don't know", "idk", "not sure", "no idea"]):
        base = encouragement[0] if encouragement else \
            "That's totally okay — this concept can be tricky! 🧠💭"
        return (
            base
            + "\n\nTry thinking about how growth is normally controlled at the molecular level. "
            + "If you'd like, you can also click **Skip / Next Question ⏭️** to move on."
        )

    # 🔹 Check which concepts are still missing
    missing = []
    for idx, concept in enumerate(key_concepts):
        if not concept_covered(concept, text):
            missing.append((idx, concept))

    # 🔹 If all concepts are covered → STOP asking new follow-ups
    if not missing:
        msg = (
            "Nice work — you've hit the key biochemical ideas for this question 💪.\n\n"
            "If you're ready, click **Skip / Next Question ⏭️** to move on, "
            "or add anything else you're curious about."
        )
        return msg

    # 🔹 Pick a follow-up aligned with the first missing concept
    first_missing_idx = missing[0][0]
    if followups and first_missing_idx < len(followups):
        return followups[first_missing_idx]

    # 🔹 Fallback if followups list is short
    return (
        "That's a solid start. Which piece still feels least clear to you — "
        "what drives the change, how control is lost, or how a mass of cells builds up?"
    )