# backend/diagram_loader.py
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Dict, Any

# Robust imports (works whether you run as package or loose files)
try:
    from backend.question_loader import ModuleBundle, QuestionPointer
except Exception:
    from question_loader import ModuleBundle, QuestionPointer


def diagram_for_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[Dict[str, Any]]:
    """
    Returns a diagram spec dict for the current question, or None.

    bundle.diagrams is loaded from modules/<module_id>/<module_id>_diagrams.json

    We key diagrams by QUESTION NUMBER (1-based) like "18".
    ptr.qi is 0-based (question index in the questions list),
    so by default qnum = ptr.qi + 1.

    If your questions include explicit numbering like "18. ...", this still works,
    because your diagrams.json can be keyed by that explicit question number.
    """
    if not getattr(bundle, "diagrams", None):
        return None

    # Try to extract "18" from the question stem if present, else fallback qi+1
    stem = ""
    try:
        stem = (bundle.questions[ptr.qi].get("q") or "")
    except Exception:
        stem = ""

    m = re.match(r"\s*(\d+)\s*[\.\)]", stem or "")
    qnum = str(int(m.group(1))) if m else str(ptr.qi + 1)

    spec = bundle.diagrams.get(qnum)
    if not isinstance(spec, dict):
        return None

    # --- Support per-subpart diagrams ---
    parts = spec.get("parts")
    if isinstance(parts, dict):
        part_letter = (getattr(ptr, "part", None) or "").strip().lower()
        if not part_letter:
            si = int(getattr(ptr, "si", 0) or 0)
            if si < 0:
                si = 0
            part_letter = chr(97 + si)

        part_spec = parts.get(part_letter)
        if isinstance(part_spec, dict):
            spec.pop("parts", None)
            spec.update(part_spec)

    spec = dict(spec)  # 👈 copy immediately
    spec.setdefault("folder", "images")

    # --- Normalize images into a dict like {"A":"file.png","B":"file.png","C":"file.png"} ---
    imgs = spec.get("images")

    # Case 1: already a dict (your current JSON)
    if isinstance(imgs, dict):
        spec["images"] = {str(k).upper(): v for k, v in imgs.items() if v}

    # Case 2: list of dicts: [{"label":"A","file":"x.png"}, ...]
    elif isinstance(imgs, list) and imgs and isinstance(imgs[0], dict):
        out: Dict[str, str] = {}
        for item in imgs:
            label = str(item.get("label", "")).upper().strip()
            filename = (item.get("file") or "").strip()
            if label and filename:
                out[label] = filename
        spec["images"] = out

    # Case 3: list of strings: ["a.png","b.png","c.png"] → auto-label A/B/C
    elif isinstance(imgs, list) and imgs and isinstance(imgs[0], str):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        spec["images"] = {letters[i]: fn for i, fn in enumerate(imgs) if fn}

    else:
        # No usable images spec
        spec["images"] = {}

    return spec


def diagram_image_path(module_id: str, spec: Dict[str, Any], filename: str) -> str:
    """
    Build a relative path usable by st.image().
    """
    folder = spec.get("folder", "images")
    return str(Path("modules") / module_id / folder / filename)
