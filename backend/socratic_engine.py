# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""
from typing import List
import re
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

def socratic_followup(module_id: str, q_index: int, student_answer: str) -> str:
    """
    Pick a single Socratic follow-up based on which key concepts are still missing
    for this (module_id, question_index). Uses BIO_CONCEPTS and <module>_answers.json.

    - Requires ALL concept_keys for that question to be covered before giving
      a mastery / move-on message.
    """
    spec_map = load_concept_keys(module_id)
    spec = spec_map.get(str(q_index + 1), {})

    concept_domain = spec.get("concept_domain", "cancer")  # default domain
    concept_keys   = spec.get("concept_keys", [])
    followups      = spec.get("followups", [])
    encouragement  = spec.get("encouragement", [])

    text = (student_answer or "").strip()
    if not text:
        return "Take a moment to jot down even a rough idea — what comes to mind first for this question?"

    lower = text.lower()

    # 🔹 Handle explicit uncertainty ("I don't know", "not sure", etc.)
    if any(phrase in lower for phrase in ["i don't know", "idk", "not sure", "no idea"]):
        base = encouragement[0] if encouragement else \
            "That's totally okay — this concept can be tricky! 🧠💭"
        return (
            base
            + "\n\nTry thinking about how growth is normally controlled at the molecular level. "
            + "If you'd like, you can also click **Skip / Next Question ⏭️** to move on."
        )

    # 🔹 Determine which concept_keys are still missing
    missing = []
    for idx, key in enumerate(concept_keys):
        if not concept_covered(concept_domain, key, text):
            missing.append((idx, key))

    # 🔹 If no concepts are missing, treat as mastery for this question
    if not missing and concept_keys:
        msg = (
            "Nice work — you've hit the key biochemical ideas for this question 💪.\n\n"
            "If you're ready, click **Skip / Next Question ⏭️** to move on, "
            "or add anything else you're curious about."
        )
        return msg

    # 🔹 If some concepts are missing, pick a follow-up aligned to the first one
    if missing:
        first_missing_idx = missing[0][0]
        if followups and first_missing_idx < len(followups):
            return followups[first_missing_idx]

    # 🔹 Fallback if followups are missing or misaligned
    generic = [
        "That's a solid start. Which piece still feels least clear — the cause, the loss of control, or how a mass of cells builds up?",
        "Good thinking so far. Can you say a bit more about what's happening at the molecular level?",
        "You're on the right track. What happens to normal control mechanisms in this situation?",
    ]
    return random.choice(generic)