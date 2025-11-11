# backend/diagram_loader.py
from typing import Optional, Dict, Any
from backend.question_loader import ModuleBundle, QuestionPointer

def _diagram_key(qi: int, si: int) -> str:
    # support several possible keys in diagrams.json:
    # "1", "1a", "1-0", "Q1", "Q1a"
    base = str(qi + 1)
    letter = chr(97 + si)  # a, b, c...
    return base, f"{base}{letter}", f"{base}-{si}", f"Q{base}", f"Q{base}{letter}"

def diagram_for_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[Dict[str, Any]]:
    d = bundle.diagrams or {}
    for key in _diagram_key(ptr.qi, ptr.si):
        if key in d and isinstance(d[key], dict):
            return d[key]
    # fallback: per-question diagram without subparts
    key = str(ptr.qi + 1)
    if key in d and isinstance(d[key], dict):
        return d[key]
    return None
