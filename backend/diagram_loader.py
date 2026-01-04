# backend/diagram_loader.py
import re
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
from question_loader import ModuleBundle, QuestionPointer

def _extract_question_number(stem: str) -> Optional[int]:
    """
    Extract the leading question number from a question stem like:
      '18) Which ...' or '18. Which ...'
    """
    m = re.match(r"\s*(\d+)\s*[\.\)]", stem or "")
    return int(m.group(1)) if m else None


def diagram_for_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[Dict[str, Any]]:
    """
    Returns diagram spec for the CURRENT question using the *printed* question number.
    Your module01_diagrams.json is keyed by "18", not by 0-based index.
    """
    if not bundle or not bundle.diagrams:
        return None

    q = bundle.questions[ptr.qi]
    stem = q.get("q", "")
    qnum = _extract_question_number(stem) or (ptr.qi + 1)  # fallback

    spec = bundle.diagrams.get(str(qnum))
    if not spec:
        return None

    module_dir = Path("modules") / bundle.module_id
    folder = spec.get("folder", "images")
    choices = spec.get("choices", [])
    correct = spec.get("correct")

    images = []
    for item in spec.get("images", []):
        label = item.get("label")
        filename = item.get("file")
        if not filename:
            continue
        path = str(module_dir / folder / filename)
        images.append({"label": label, "file": filename, "path": path})

    return {
        "qnum": qnum,  # ✅ important for stable widget keys
        "prompt": spec.get("prompt", ""),
        "choices": choices,
        "correct": correct,
        "folder": folder,
        "images": images,
    }


def diagram_image_path(module_id: str, spec: Dict[str, Any], filename: str) -> str:
    """
    Build a relative path usable by st.image.
    """
    folder = spec.get("folder", "images")
    return str(Path("modules") / module_id / folder / filename)
