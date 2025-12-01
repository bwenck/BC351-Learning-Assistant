# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""
from typing import List
import re
import random
from backend.question_loader import load_concept_keys
from biochem_concepts import BIO_CONCEPTS

# ---------------------------------------------------------
# 🔍Smart semantic matching for key concepts
# ---------------------------------------------------------

def concept_covered(domain: str, concept_key: str, student_answer: str) -> bool:
    """
    Returns True if the student's answer covers the named concept,
    using BIO_CONCEPTS[domain][concept_key] as a list of variant phrases.

    We treat a concept as 'covered' if at least one meaningful word
    from the concept or its variants appears in the student's answer.
    """
    student = student_answer.lower()

    domain_map = BIO_CONCEPTS.get(domain, {})
    variants = domain_map.get(concept_key, [])

    # Build list of phrases to search: key itself + any variant strings
    phrases = [concept_key.lower()] + [
        v.lower() for v in variants if isinstance(v, str)
    ]

    for phrase in phrases:
        # Break into words and keep non-trivial ones
        words = [w for w in re.findall(r"[a-zA-Z]+", phrase) if len(w) > 3]
        if not words:
            continue

        # If at least one of these words appears in the student's answer,
        # we count this concept as covered.
        for w in words:
            if w in student:
                return True

    return False

def socratic_followup(module_id: str, qid: int, student_answer: str):
    """
    Returns ONE Socratic follow-up question based on missing concepts.
    If all required concepts are satisfied → return None (signal to advance).
    """

    missing_required, missing_optional, spec = evaluate_concepts(
        module_id, qid, student_answer
    )

    # If nothing key is missing → no follow-up needed
    if not missing_required:
        return None

    # Pick one missing concept
    concept = missing_required[0]

    # Encouragement + concept-specific follow-up
    encouragement = choice(spec["encouragement"])
    followup = spec["followups"][concept]

    return f"{encouragement} {followup}"