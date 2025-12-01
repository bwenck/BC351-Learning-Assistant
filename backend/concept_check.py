# backend/concept_check.py
from typing import List
import re
import json
from pathlib import Path
from functools import lru_cache
from biochem_concepts import BIO_CONCEPTS

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().strip())

def concept_hit(concept: str, student_answer: str, domain: str | None = None) -> bool:
    """
    Check whether a concept is covered in the student's answer.
    Uses:
      - the concept phrase itself
      - any synonyms/variants from BIO_CONCEPTS[domain][concept]
    Matching is done on simple word stems, so:
      'proliferation' ~ 'proliferative' (proli…)
      'uncontrolled division' ~ 'cells divide uncontrollably' (uncon…, divid…)
    """
    student = student_answer.lower()

    # Build a list of phrases to check: base concept + synonyms from BIO_CONCEPTS
    phrases = [concept]
    if domain and domain in BIO_CONCEPTS:
        variants = BIO_CONCEPTS[domain].get(concept, [])
        phrases.extend(variants)

    # If nothing to check, bail
    phrases = [p for p in phrases if p]
    if not phrases:
        return False

    # If ANY variant’s key stems are all present in the answer → concept is covered
    for phrase in phrases:
        words = [w for w in re.findall(r"[a-z]+", phrase.lower()) if len(w) > 4]
        stems = [w[:5] for w in words]
        if stems and all(stem in student for stem in stems):
            return True

    return False

@lru_cache(maxsize=16)
def load_answer_spec(module_id: str):
    path = Path(f"modules/{module_id}/{module_id}_answers.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text())

def evaluate_concepts(module_id: str, qid: int, student_answer: str):
    """
    Returns:
      missing_required: list[str]
      missing_optional: list[str]
      spec: full JSON entry for this question
    """
    json_path = Path(f"modules/{module_id}/{module_id}_answers.json")
    data = json.loads(json_path.read_text())

    spec = data[str(qid)]
    domain = spec.get("concept_domain")  # e.g. "cancer"

    required = spec.get("required_concepts", [])
    optional = spec.get("optional_concepts", [])

    missing_required = [
        c for c in required
        if not concept_hit(c, student_answer, domain)
    ]
    missing_optional = [
        c for c in optional
        if not concept_hit(c, student_answer, domain)
    ]

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