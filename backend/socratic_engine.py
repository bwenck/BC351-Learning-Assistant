# backend/socratic_engine.py
"""
This version keeps a minimal interface so your app stays fast.
We DON’T generate new concepts; we only rephrase a focused question if needed.
Concept-grounded Socratic followups driven by moduleXX_answers.json.

Returns:
  - str follow-up message, or
  - None if all required concepts are covered (so UI can advance)
"""
from typing import List
import re
import random
import streamlit as st
from concept_check import evaluate_concepts, is_uncertain, is_gibberish
from biochem_concepts import BIO_CONCEPTS

# ---------------------------------------------------------
# 🔍Smart semantic matching for key concepts
# ---------------------------------------------------------

def uncertainty_message(spec: dict) -> str:
    follow = (spec or {}).get(
        "uncertainty_followup",
        "Take a moment to jot down even a rough idea — what comes to mind?"
    ).strip()
    return (
        "That's totally okay — this concept can be tricky! 🧠💭\n"
        f"{follow}\n\n"
        "If you'd like, you can also click **Skip / Next Question ⏭️** to move on."
    )

def gibberish_message() -> str:
    return (
        "I couldn’t understand that response.\n"
        "Try again using a short sentence (a few real words), or click **Skip / Next Question ⏭️**."
    )

def socratic_followup(
    module_id: str,
    qid: int,                 # 0-based
    student_answer: str,      # combined text so far
    latest_answer: str = "",
    *,
    part_idx: int = 0,        # 0->a, 1->b, ...
    stem: str = "",
    uncertain_now: bool = False,
    uncertain_count: int = 0,
    gibberish_now: bool = False,
    gibberish_count: int = 0,
):
    text = (student_answer or "").strip()
    latest = (latest_answer or "").strip()

    # 1) Pull concept spec + missing concepts
    # ✅ qid stays 0-based here.
    # ✅ part_idx is passed if concept_check supports it; otherwise we fall back cleanly.
    try:
        missing_required, _missing_optional, spec = evaluate_concepts(
            module_id,
            qid,
            text,
            part_idx=part_idx,
            stem=stem,
        )
    except TypeError:
        # Older concept_check.evaluate_concepts signature (no part_idx)
        missing_required, _missing_optional, spec = evaluate_concepts(module_id, qid, text)

    # 2) ✅ Gibberish guardrail (ONLY based on latest submission)
    if gibberish_now:
        if gibberish_count >= 1:
            return (
                "Still not quite readable — let's keep moving.\n"
                "Click **Skip / Next Question ⏭️** when you're ready."
            )
        return gibberish_message()

    # 3) ✅ Uncertainty guardrail (ONLY based on latest submission)
    if uncertain_now:
        if uncertain_count >= 1:
            return (
                "That's totally okay — sometimes it's best to keep moving. "
                "If you'd like, click **Skip / Next Question ⏭️** when you're ready."
            )
        return uncertainty_message(spec)

    # 4) If no spec exists, fall back
    if not spec:
        return "Nice start — can you add one more molecular detail?"

    # If they used a known wrong numeric answer, ask the targeted follow-up.
    # Only run this if we *still* have missing required concepts.
    wrong_triggers = spec.get("wrong_triggers", {}) or {}
    if missing_required and isinstance(wrong_triggers, dict):
        for wrong_val, prompts in wrong_triggers.items():
            wrong_s = str(wrong_val).strip()
            if wrong_s and re.search(rf"(?<!\d){re.escape(wrong_s)}(?!\d)", latest):
                # pick a follow-up prompt tied to that wrong value
                if isinstance(prompts, list) and prompts:
                    follow_text = random.choice(prompts)
                elif isinstance(prompts, str) and prompts.strip():
                    follow_text = prompts.strip()
                else:
                    follow_text = ""

                if follow_text:
                    encouragement_list = spec.get("encouragement", []) or []
                    encouragement = (
                        random.choice(encouragement_list)
                        if encouragement_list
                        else "Keep going — you're on the right track."
                    )
                    return f"{encouragement} {follow_text}"

    # 5) If all REQUIRED concepts covered → advance
    if not missing_required:
        return None

    # 6) Ask targeted followup
    concept = missing_required[0]
    encouragement_list = spec.get("encouragement", []) or []
    encouragement = random.choice(encouragement_list) if encouragement_list else "Keep going — you're on the right track."

    followups_map = spec.get("followups", {}) or {}
    follow_entry = followups_map.get(concept)

    if isinstance(follow_entry, list):
        follow_text = random.choice(follow_entry) if follow_entry else ""
    else:
        follow_text = follow_entry or ""

    if not follow_text:
        follow_text = "What part of the mechanism is still unclear?"

    return f"{encouragement} {follow_text}"
