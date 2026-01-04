# backend/diagram_loader.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any

from question_loader import ModuleBundle, QuestionPointer


def diagram_for_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[Dict[str, Any]]:
    """
    Returns a diagram spec for the current question, or None.

    bundle.diagrams is loaded from modules/<module_id>/<module_id>_diagrams.json

    We key diagrams by *question number* (1-based) to match the student's question numbering.
    ptr.qi is 0-based, so qnum = ptr.qi + 1.
    """
    if not getattr(bundle, "diagrams", None):
        return None

    qnum = str(ptr.qi + 1)
    spec = bundle.diagrams.get(qnum)
    if not isinstance(spec, dict):
        return None

    # default folder (your repo uses /images)
    spec = dict(spec)  # shallow copy so we can enrich safely
    spec.setdefault("folder", "images")

    # normalize images map if present
    imgs = spec.get("images")
    if isinstance(imgs, dict):
        # ensure keys are "A","B","C" etc
        spec["images"] = {str(k).upper(): v for k, v in imgs.items()}

    return spec


def diagram_image_path(module_id: str, spec: Dict[str, Any], filename: str) -> str:
    """
    Build a relative path usable by st.image.
    """
    folder = spec.get("folder", "images")
    return str(Path("modules") / module_id / folder / filename)
