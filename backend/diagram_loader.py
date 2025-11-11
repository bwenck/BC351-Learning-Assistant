from typing import Optional, Dict, Any
from backend.question_loader import ModuleBundle, QuestionPointer

def diagram_for_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[Dict[str, Any]]:
    # Expect diagrams.json like:
    # {
    #   "q1": {"image": "image_A.png", "prompt": "Which is amphoteric?", "choices": ["A","B","C"]},
    #   "q1b": {...}, "q2": {...},
    #   "bonus_question": "Why does ...?"
    # }
    key = f"q{ptr.qi+1}"
    if ptr.si > 0:
        key += chr(97+ptr.si)  # a, b, c...
    d = bundle.diagrams.get(key)
    return d if isinstance(d, dict) else None
