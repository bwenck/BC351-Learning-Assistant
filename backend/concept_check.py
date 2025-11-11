# backend/concept_check.py
from typing import List
import re

_STOP = {
    "the","a","an","and","or","but","of","in","on","by","to","for","with","as",
    "that","this","these","those","from","into","at","is","are","was","were",
    "be","being","been","it","its","their","there","which","what","when","how",
    "why","do","does","did","can","could","should","would","about","such"
}
_SPLIT = re.compile(r"[.\n;!?]+")

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def _tokens(s: str) -> List[str]:
    return [w for w in re.findall(r"[a-z0-9\-]+", s.lower()) if w and w not in _STOP]

def extract_concepts_from_answer(answer_block: str, max_concepts: int = 6) -> List[str]:
    seen = set()
    concepts: List[str] = []
    for sent in _SPLIT.split(answer_block or ""):
        s = _normalize(sent)
        if len(s) < 20:
            continue
        toks = [t for t in _tokens(s) if len(t) >= 4]
        if not toks:
            continue
        phrase = " ".join(toks[:5])
        key = " ".join(toks[:2]) if len(toks) >= 2 else phrase
        if key and key not in seen:
            seen.add(key)
            concepts.append(phrase)
        if len(concepts) >= max_concepts:
            break
    return concepts

def missing_concepts(answer_block: str, student_answer: str) -> List[str]:
    reply_toks = set(_tokens(_normalize(student_answer)))
    misses: List[str] = []
    for concept in extract_concepts_from_answer(answer_block):
        ctoks = set(_tokens(concept))
        if not ctoks.issubset(reply_toks):
            misses.append(concept)
    return misses

def make_followup(question_text: str, concept_phrase: str) -> str:
    base = concept_phrase.split()[:4]
    cue = " ".join(base)
    return f"What role does {cue} have in your answer to: “{question_text}”?"
