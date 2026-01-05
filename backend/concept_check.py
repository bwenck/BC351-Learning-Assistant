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

_WORD = re.compile(r"[a-zA-Z]{2,}")

def is_gibberish(text: str) -> bool:
    """
    Heuristic: catches keyboard mashing / random strings.
    Returns True for low-signal inputs like 'sljgf;lsdakjfg'.
    """
    t = (text or "").strip()
    if not t:
        return True

    # very short answers aren't necessarily gibberish ("idk" is uncertainty)
    if len(t) < 4:
        return False

    # If it contains "idk"/"don't know" etc, let uncertainty logic handle it
    if is_uncertain(t):
        return False

    # Ratio of alphabetic characters
    letters = sum(ch.isalpha() for ch in t)
    if letters / max(1, len(t)) < 0.5:
        return True

    # Tokenize into "words"
    words = _WORD.findall(t.lower())
    if len(words) == 0:
        return True

    # Keyboard mash tends to be 1 long "word" with few vowels
    vowels = sum(ch in "aeiou" for ch in t.lower())
    if len(t) >= 10 and vowels / max(1, letters) < 0.25:
        return True

    # If the average "word" is extremely long and there are very few words
    if len(words) <= 1 and max(len(w) for w in words) >= 12:
        return True

    return False
