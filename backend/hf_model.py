# backend/hf_model.py
"""
Fast, model-light “Socratic” grounded engine.

- init_hf(): returns a placeholder (no heavy model needed)
- hf_socratic(): produces ONE focused follow-up grounded in the official answer text
                 by using concept extraction (no hallucination)
This keeps Streamlit Cloud fast and free.
"""

from typing import Any
from backend.concept_check import missing_concepts, make_followup
from backend.question_loader import load_module_bundle

def init_hf() -> Any:
    # placeholder for future true-HF client if you decide to add one
    return {"engine": "concept-grounded"}

def hf_socratic(llm: Any, module_id: str, question_index: int, student_answer: str, notes_context: str = "") -> str:
    """
    Compute a grounded follow-up:
      - pull the official answer text for this question
      - detect missing concepts vs student's reply
      - if missing: ask a single targeted follow-up about the first missing concept
      - if none missing: return a gentle transition prompt (the app advances the pointer)
    """
    bundle = load_module_bundle(module_id)

    # Get official answer text for this question
    try:
        ans_block_list = bundle.answers[question_index]  # list[str]
        official_answer_text = " ".join(ans_block_list) if isinstance(ans_block_list, list) else str(ans_block_list or "")
    except Exception:
        official_answer_text = ""

    q_text = bundle.question_text(bundle.questions and type("Ptr", (), {"qi": question_index, "si": 0}) or None) \
             if hasattr(bundle, "question_text") else ""

    # Determine missing concepts
    misses = missing_concepts(official_answer_text, student_answer)

    if misses:
        return make_followup(q_text or f"question {question_index+1}", misses[0])

    # No concepts missing — return a short transition notice; the app will advance pointer
    return "Nice — once you’re ready, continue to the next part."
