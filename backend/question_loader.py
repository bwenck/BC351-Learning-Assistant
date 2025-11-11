# backend/question_loader.py
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Dict, Any
import json


# ---------- Data structures expected by the app ----------

@dataclass
class QuestionPointer:
    """Pointer to a specific subpart of a question (0-based)."""
    qi: int          # question index
    si: int          # subpart index (0 = first subpart). If a question has no subparts, si is always 0.


@dataclass
class ModuleBundle:
    """All content for a module, plus helper methods used by the UI."""
    module_id: str
    title: str
    questions: List[Dict[str, Any]]   # [{"q": str, "parts": [str, ...]}, ...]
    answers: List[List[str]]          # parallel to questions (optional)
    notes: List[str]                  # extra context or metadata
    diagrams: Dict[str, Any]          # optional diagrams.json contents

    # --- Helpers the UI calls ---

    def question_text(self, ptr: QuestionPointer) -> str:
        """Return the display text for the current subpart (or the main stem if no subparts)."""
        q = self.questions[ptr.qi]
        parts: List[str] = q.get("parts", [])
        if parts:
            # subparts exist; clamp si
            si = max(0, min(ptr.si, len(parts) - 1))
            body = parts[si].strip()
            # strip leading "a)"/"b)" if present for cleaner UI
            if len(body) > 2 and body[1] == ')' and body[0].isalpha():
                body = body[2:].strip()
            label = f"{ptr.qi+1}{chr(97+si)}) "
            return label + body
        else:
            stem = q["q"].strip()
            # strip "1." / "2)" etc from the stem
            while stem and (stem[0].isdigit() or stem[0] in ")."):
                stem = stem[1:].lstrip()
            return f"{ptr.qi+1}) " + (stem or "(empty)")

    def subparts_count(self, qi: int) -> int:
        """Return number of subparts for question qi (0 if none). For UI we use max(1, count)."""
        if qi < 0 or qi >= len(self.questions):
            return 1
        parts = self.questions[qi].get("parts", [])
        return max(1, len(parts))  # ensure at least 1 step per question

    def context_snips_for(self, ptr: QuestionPointer, k: int = 3) -> List[str]:
        """Short, safe snippets from nearby questions (never answers)."""
        snips: List[str] = []
        for off in range(-1, 2):
            idx = ptr.qi + off
            if 0 <= idx < len(self.questions):
                q = self.questions[idx]
                # combine stem + first subpart if present
                stem = q.get("q", "")
                part0 = (q.get("parts") or [""])[0]
                snippet = (stem + " " + part0).strip()[:160]
                if snippet:
                    snips.append(snippet)
        return snips

    def bonus_question(self) -> Optional[str]:
        """Look for a bonus question in diagrams.json or notes (line starting with 'BONUS:')."""
        b = self.diagrams.get("bonus_question") if isinstance(self.diagrams, dict) else None
        if isinstance(b, str) and b.strip():
            return b.strip()
        for line in reversed(self.notes or []):
            if line.strip().lower().startswith("bonus:"):
                return line.split(":", 1)[1].strip()
        return None


# ---------- Parsing & loading ----------

def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

def _parse_qa_lines(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Parse text into a list of {"q": stem, "parts": [subparts]}.
    Stem line starts with "1."/"2)" etc. Subparts start with "a)"/"b)"/"c)".
    Continuation lines are appended to the last segment.
    """
    out: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    def is_q(line: str) -> bool:
        return bool(line and line[0].isdigit() and (("." in line[:3]) or (")" in line[:3])))

    def is_sub(line: str) -> bool:
        if len(line) < 2:
            return False
        a = line[:2].lower()
        return a in ("a)", "b)", "c)", "d)", "e)", "f)")

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if is_q(line):
            if current:
                out.append(current)
            current = {"q": line, "parts": []}
        elif current and is_sub(line):
            current["parts"].append(line)
        elif current:
            # continuation
            if current["parts"]:
                current["parts"][-1] = (current["parts"][-1] + " " + line).strip()
            else:
                current["q"] = (current["q"] + " " + line).strip()
        else:
            # orphan line before first question — start a synthetic question
            current = {"q": line, "parts": []}

    if current:
        out.append(current)
    return out


@lru_cache(maxsize=16)
def load_module_bundle(module_id: str) -> ModuleBundle:
    """
    Load module content using your naming convention:
      modules/<module_id>/<module_id>_questions.txt
      modules/<module_id>/<module_id>_answers.txt
      modules/<module_id>/<module_id>_notes.txt       (optional)
      modules/<module_id>/<module_id>_diagrams.json   (optional)
      modules/<module_id>/images/                     (optional)
    """
    mdir = Path("modules") / module_id
    if not mdir.exists():
        raise FileNotFoundError(f"Module folder not found: {mdir}")

    q_file = mdir / f"{module_id}_questions.txt"
    a_file = mdir / f"{module_id}_answers.txt"
    n_file = mdir / f"{module_id}_notes.txt"
    d_file = mdir / f"{module_id}_diagrams.json"
    t_file = mdir / "title.txt"  # optional human-friendly title

    q_lines = _read_lines(q_file)
    if not q_lines:
        raise ValueError(f"❌ No questions found for module '{module_id}'. Check {q_file.name}")

    questions = _parse_qa_lines(q_lines)

    # answers parallel format is optional; if not structured, keep simple lists
    a_lines = _read_lines(a_file)
    # group answers in the same number of questions (best effort)
    answers_grouped: List[List[str]] = []
    if a_lines:
        # simple grouping: split by blank lines (or "1.", "2.)" headings if present)
        current: List[str] = []
        for ln in a_lines:
            if ln and ln[0].isdigit() and (("." in ln[:3]) or (")" in ln[:3])):
                if current:
                    answers_grouped.append(current)
                    current = []
                current = [ln]
            else:
                current.append(ln)
        if current:
            answers_grouped.append(current)
        # pad or trim to match question count
        while len(answers_grouped) < len(questions):
            answers_grouped.append([])
        if len(answers_grouped) > len(questions):
            answers_grouped = answers_grouped[:len(questions)]
    else:
        answers_grouped = [[] for _ in questions]

    notes = _read_lines(n_file)
    diagrams: Dict[str, Any] = {}
    if d_file.exists():
        try:
            diagrams = json.loads(d_file.read_text(encoding="utf-8"))
        except Exception:
            diagrams = {}

    title = t_file.read_text(encoding="utf-8").strip() if t_file.exists() else module_id

    return ModuleBundle(
        module_id=module_id,
        title=title,
        questions=questions,
        answers=answers_grouped,
        notes=notes,
        diagrams=diagrams,
    )


# ---------- Navigation helper the UI imports ----------

def next_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[QuestionPointer]:
    """Advance to next subpart; if none, move to next question; return None at end."""
    qi, si = ptr.qi, ptr.si
    count = bundle.subparts_count(qi)
    si += 1
    if si < count:
        return QuestionPointer(qi, si)
    # next question
    qi += 1
    if qi < len(bundle.questions):
        # start at first subpart if any; else 0
        first_count = bundle.subparts_count(qi)
        return QuestionPointer(qi, 0 if first_count > 0 else 0)
    return None

# ---------- Empty bundle helper for initial state ----------

@staticmethod
def empty() -> "ModuleBundle":
    """Return a placeholder module bundle with no questions yet."""
    return ModuleBundle(
        module_id="none",
        title="No module loaded",
        questions=[{"q": "(no questions loaded)", "parts": []}],
        answers=[[]],
        notes=[],
        diagrams={}
    )
