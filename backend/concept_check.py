# backend/concept_check.py
from typing import List
import re
import json
from pathlib import Path
from functools import lru_cache
from biochem_concepts import BIO_CONCEPTS

print("✅ concept_check.py loaded (v2025-11-xx qid+1 fix)")

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().strip())

def concept_hit(concept: str, student_answer: str, domain: str | None = None) -> bool:
    """
    Returns True if the student's answer matches a concept,
    using the base phrase + any variants from BIO_CONCEPTS[domain].
    """
    student = student_answer.lower()

    # collect all phrases to test: main concept + variants
    phrases = [concept]
    if domain and domain in BIO_CONCEPTS:
        phrases.extend(BIO_CONCEPTS[domain].get(concept, []))

    phrases = [p for p in phrases if p]
    if not phrases:
        return False

    for phrase in phrases:
        words = [w for w in re.findall(r"[a-z]+", phrase.lower()) if len(w) > 4]
        stems = [w[:5] for w in words]  # crude stemming
        if stems and all(stem in student for stem in stems):
            return True

    return False

@lru_cache(maxsize=16)
def load_concept_spec(module_id: str):
    path = Path(f"modules/{module_id}/{module_id}_answers.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate_concepts(module_id: str, qid: int, student_answer: str):
    spec_all = load_concept_spec(module_id)

    # JSON keys are "1","2","3"... but internal qid is 0-based.
    spec = spec_all.get(str(qid + 1))
    if not isinstance(spec, dict):
        return [], [], {}

    domain = spec.get("concept_domain")
    required = spec.get("required_concepts", []) or []
    optional = spec.get("optional_concepts", []) or []

    missing_required = [c for c in required if not concept_hit(c, student_answer, domain)]
    missing_optional = [c for c in optional if not concept_hit(c, student_answer, domain)]

    return missing_required, missing_optional, spec

def is_uncertain(text: str) -> bool:
    """
    Detects when a student expresses uncertainty.
    """
    t = text.strip().lower()
    unsure = [
        "i don't know",
        "idk",
        "not sure",
        "i am not sure",
        "no idea",
        "i'm unsure",
        "unsure",
        "i'm confused",
        "i am confused"
    ]
    return any(u in t for u in unsure)