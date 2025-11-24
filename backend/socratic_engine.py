# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""
from typing import List
import re
from backend.question_loader import load_concept_keys

# ---------------------------------------------------------
# 🔍 NEW: Smarter semantic matching for key concepts
# ---------------------------------------------------------
def concept_covered(concept: str, student_answer: str) -> bool:
    """
    Returns True if the student's answer semantically matches the concept.
    Uses keyword stems and loose matching instead of exact text match.
    """
    student = student_answer.lower()
    concept = concept.lower()

    # Extract word stems (mutat, prolifer, regulat, signal, tumor, etc)
    key_stems = re.findall(r"[a-zA-Z]+", concept)
    key_stems = [stem[:5] for stem in key_stems if len(stem) > 4]

    # Require each stem to match *somewhere in the student's answer*
    return all(stem in student for stem in key_stems)

def socratic_followup(module_id, q_index, student_answer):
    concepts = load_concept_keys(module_id).get(str(q_index+1), {})
    keys = concepts.get("key_concepts", [])
    followups = concepts.get("followups", [])
    encouragements = concepts.get("encouragement", [])

    text = student_answer.lower()

    # Detect missing concepts
    missing = []
    for concept in keys:
        if not concept_covered(concept, student_answer):
            missing.append(concept)

    # If student said they don't know or similar
    if any(p in text for p in ["idk", "don't know", "not sure", "help"]):
        return (
            (encouragements or ["Take your time — you're learning! 😊"])[0]
            + " Want a hint or to move on?"
        )

    # If none missing, move on
    if not missing:
        return "Nice thinking — ready for the next question? ✅"

    # If missing, return the NEXT hint only
    idx = len(keys) - len(missing)
    idx = min(idx, len(followups)-1)

    return followups[idx]