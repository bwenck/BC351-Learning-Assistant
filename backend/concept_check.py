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

    # numeric concept support (e.g., "6.0", "9.2", "1.8")
    if any(ch.isdigit() for ch in (concept or "")):
        nums = re.findall(r"\d+(?:\.\d+)?", concept)
        if nums:
            # if any required number is missing, fail
            if not all(n in student for n in nums):
                return False

            # ✅ if the concept is basically just a number (no letters), accept immediately
            if not re.search(r"[a-zA-Z]", concept):
                return True

    # ✅ short-phrase support (e.g., "more than half", "net charge")
    norm_concept = normalize(concept)
    norm_student = normalize(student_answer)

    # If the concept is short / has no long words, allow direct phrase match
    words = re.findall(r"[a-zA-Z]+", norm_concept)
    long_words = [w for w in words if len(w) > 4]

    if norm_concept and (norm_concept in norm_student) and (len(long_words) == 0):
        return True

    # collect all phrases to test: main concept + variants
    phrases = [concept]
    if domain and domain in BIO_CONCEPTS:
        phrases.extend(BIO_CONCEPTS[domain].get(concept, []))

    phrases = [p for p in phrases if p]
    if not phrases:
        return False

    CHEM_TOKENS = {"cooh", "nh3", "nh2", "nterm", "cterm", "imidazole"}  # extend as needed

    for phrase in phrases:
        pl = phrase.lower()

        # 1) Original long-word stem match (unchanged behavior)
        words = [w for w in re.findall(r"[a-z]+", pl) if len(w) > 4]
        stems = [w[:5] for w in words]
        long_ok = stems and all(stem in student for stem in stems)

        # 2) NEW: short chemistry token match (only if present in the phrase)
        # Normalize student so NH3+ matches as 'nh3'
        student_norm = re.sub(r"[^a-z0-9]+", "", student)
        phrase_norm = re.sub(r"[^a-z0-9]+", "", pl)

        token_hits = []
        for tok in CHEM_TOKENS:
            if tok in phrase_norm:
                token_hits.append(tok in student_norm)

        short_ok = (len(token_hits) > 0) and all(token_hits)

        if long_ok or short_ok:
            return True

    return False

@lru_cache(maxsize=16)
def load_concept_spec(module_id: str):
    path = Path(f"modules/{module_id}/{module_id}_answers.json")
    print("📌 loading answers spec from:", path.resolve(), "exists:", path.exists())
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def evaluate_concepts(module_id: str, qid: int, student_answer: str, part_idx: int = 0, stem: str | None = None):
    """
    qid is 0-based question index from pointer (0,1,2,...)

    If stem starts with an explicit question number like "21.", we use that number
    to find JSON keys like "21a", "21b", etc.
    Otherwise we fall back to qid+1.
    """
    spec_all = load_concept_spec(module_id)

    # --- Prefer explicit question number from the stem ("21.", "21)", etc.) ---
    qnum_from_stem = None
    if stem:
        m = re.match(r"\s*(\d+)\s*[\.\)]", stem.strip())
        if m:
            qnum_from_stem = int(m.group(1))

    qnum_str = str(qnum_from_stem if qnum_from_stem is not None else (qid + 1))

    # Subpart letter
    pi = int(part_idx or 0)
    if pi < 0:
        pi = 0
    letter = chr(97 + pi)  # 0->a,1->b,...

    part_key = f"{qnum_str}{letter}"
    spec = spec_all.get(part_key)
    if not isinstance(spec, dict):
        spec = spec_all.get(qnum_str)

    if not isinstance(spec, dict):
        return [], [], {}

    domain = spec.get("concept_domain")
    required = spec.get("required_concepts", []) or []
    optional = spec.get("optional_concepts", []) or []

    missing_required = [c for c in required if not concept_hit(c, student_answer, domain)]
    missing_optional = [c for c in optional if not concept_hit(c, student_answer, domain)]
    print("🔎 looking for keys:", part_key, "or", qnum_str, "available:", list(spec_all.keys())[:15])

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
