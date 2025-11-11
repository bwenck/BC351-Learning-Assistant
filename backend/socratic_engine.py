# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
"""

from typing import List

def socratic_followup(question_text: str, student_answer: str, context_snips: List[str]) -> str:
    """
    A tiny safety net if you ever want a model-less fallback:
    - If student's answer is empty → ask a gentle probe
    - Else ask a short mechanism question tied to the current question text
    (Your app now prefers concept-based follow-ups via hf_model.py)
    """
    ans = (student_answer or "").strip().lower()
    if not ans:
        return "What initial molecular idea comes to mind here?"

    # very short, non-leading probe that stays on mechanism
    return f"What specific molecular mechanism relates to “{question_text}”?"
