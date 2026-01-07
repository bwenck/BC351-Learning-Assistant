# backend/question_loader.py
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Dict, Any
import json
import re

@dataclass
class QuestionPointer:
    """Pointer to specific question/subpart (0-based indices)."""
    qi: int  # question index
    si: int  # subpart index (0 if none)
    part: str | None = None  # NEW: "a", "b", "e", etc.

@dataclass
class ModuleBundle:
    """All content for a module."""
    module_id: str
    title: str
    questions: List[Dict[str, Any]]   # [{"q": stem, "parts": [...]}]
    answers: List[List[str]]          # parallel structure (best-effort per Q)
    notes: List[str]                  # lines from *_notes.txt (optional)
    diagrams: Dict[str, Any]          # from *_diagrams.json (optional)

    # ---------- UI helpers ----------
    def question_text(self, ptr: QuestionPointer) -> str:
        q = self.questions[ptr.qi]
        parts: List[str] = q.get("parts", [])
        if parts:
            si = max(0, min(ptr.si, len(parts) - 1))
            body = parts[si].strip()
            # remove leading "a)"/"b)" if present for display
            if len(body) > 2 and body[1] == ')' and body[0].isalpha():
                body = body[2:].strip()
            label = f"{ptr.qi+1}{chr(97+si)}) "
            return label + (body or "(empty)")
        else:
            stem = q.get("q", "").strip()
            # strip "1." / "2)" etc
            stem = re.sub(r"^\s*[\d]+\s*[\.\)]\s*", "", stem)
            return f"{ptr.qi+1}) " + (stem or "(empty)")

    def subparts_count(self, qi: int) -> int:
        if qi < 0 or qi >= len(self.questions):
            return 1
        parts = self.questions[qi].get("parts", [])
        return max(1, len(parts))

    def context_snips_for(self, ptr: QuestionPointer, k: int = 3) -> List[str]:
        """Short question-only snippets (never answers)."""
        snips: List[str] = []
        for off in range(-1, 2):
            idx = ptr.qi + off
            if 0 <= idx < len(self.questions):
                q = self.questions[idx]
                stem = q.get("q", "")
                part0 = (q.get("parts") or [""])[0]
                snippet = (stem + " " + part0).strip()[:160]
                if snippet:
                    snips.append(snippet)
        return snips[:k]

    def bonus_question(self) -> Optional[str]:
        # diagrams.json can optionally include: {"bonus_question": "..."}
        if isinstance(self.diagrams, dict):
            b = self.diagrams.get("bonus_question")
            if isinstance(b, str) and b.strip():
                return b.strip()
        # or notes may contain line starting "BONUS: ..."
        for line in reversed(self.notes or []):
            if line.strip().lower().startswith("bonus:"):
                return line.split(":", 1)[1].strip()
        return None

    # static empty bundle for boot
    @staticmethod
    def empty():
        return ModuleBundle(
            module_id="(none)",
            title="No module loaded",
            questions=[{"q": "(session not started yet)", "parts": []}],
            answers=[[]],
            notes=[],
            diagrams={}
        )

# ---- Load structured concept answers ----

@lru_cache(maxsize=16)
def load_concept_keys(module_id: str):
    path = Path(f"modules/{module_id}/{module_id}_answers.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

# ---------- Parsing & loading ----------

def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()]

_Q_LINE = re.compile(r"^\s*\d+\s*[\.\)]\s*")      # "1. " or "1) "
_SUB_LINE = re.compile(r"^\s*[a-fA-F]\s*[\.\)]\s*") 
_INLINE_PART_RE = re.compile(r"(?<!\w)([a-z])[\.\)]\s+", re.IGNORECASE)

def _split_inline_parts(text: str):
    """
    Split a single line that contains inline parts like:
      '... a. ... b. ... c. ...'
    Returns: (stem_text, parts_list) where parts_list is [{"id":"a","text":"..."}, ...]
    If no inline parts found, returns (text, []).
    """
    s = (text or "").strip()
    matches = list(_INLINE_PART_RE.finditer(s))
    if not matches:
        return s, []

    # stem is everything before first 'a.' / 'b.' marker
    first = matches[0]
    stem = s[: first.start()].strip()

    parts = []
    for i, m in enumerate(matches):
        letter = m.group(1).lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(s)
        part_text = s[start:end].strip(" \t-:;")
        if part_text:
            parts.append({"id": letter, "text": part_text})

    return stem, parts

def _parse_qa_lines(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Convert text into [{"q": stem, "parts": [subparts...]}].
    - New question when line starts with "1." or "1)" etc
    - Subpart when line starts with "a)"..."f)" or "a."..."f."
    - Continuation lines are appended to the previous segment

    NEW: If the question stem line contains inline parts like "a. ... b. ... c. ...",
         we split those into cur["parts"] immediately so parts advance one-at-a-time.
    """
    out: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None

    # Inline-part splitter: finds "a." / "b)" etc *inside* a line
    _INLINE_PART_RE = re.compile(r"(?<!\w)([a-z])[\.\)]\s+", re.IGNORECASE)

    def _split_inline_parts(text: str):
        """
        If text contains inline 'a. ... b. ...', return (stem, [part1, part2, ...])
        where each part is stored as a normal subpart line like "a) ...".
        If none found, return (text, []).
        """
        s = (text or "").strip()
        matches = list(_INLINE_PART_RE.finditer(s))
        if not matches:
            return s, []

        stem = s[: matches[0].start()].strip()

        parts: List[str] = []
        for i, m in enumerate(matches):
            letter = m.group(1).lower()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(s)
            body = s[start:end].strip(" \t-:;")
            if body:
                # store in the same style your parser already expects for subparts
                parts.append(f"{letter}) {body}")

        return stem, parts

    def is_q(line: str) -> bool:
        return bool(_Q_LINE.match(line))

    def is_sub(line: str) -> bool:
        return bool(_SUB_LINE.match(line))

    started = False

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if is_q(line):
            started = True
            if cur:
                out.append(cur)

            # ✅ NEW: split inline a/b/c... if they exist in the question line
            stem, inline_parts = _split_inline_parts(line)
            cur = {"q": stem, "parts": []}
            if inline_parts:
                cur["parts"].extend(inline_parts)

            continue

        if not started:
            continue

        if cur and is_sub(line):
            cur["parts"].append(line)
        elif cur:
            # continuation
            if cur["parts"]:
                cur["parts"][-1] = (cur["parts"][-1] + " " + line).strip()
            else:
                cur["q"] = (cur["q"] + " " + line).strip()
        else:
            cur = {"q": line, "parts": []}

    if cur:
        out.append(cur)

    return out

def _group_answers(answer_lines: List[str], q_count: int) -> List[List[str]]:
    """
    Best-effort grouping of answers per question.
    Splits on "1."/"1)" style headings; keeps text blocks otherwise.
    """
    if not answer_lines:
        return [[] for _ in range(q_count)]
    groups: List[List[str]] = []
    cur: List[str] = []
    for ln in answer_lines:
        if _Q_LINE.match(ln):
            if cur:
                groups.append(cur)
                cur = []
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        groups.append(cur)
    # pad/trim to match question count
    while len(groups) < q_count:
        groups.append([])
    if len(groups) > q_count:
        groups = groups[:q_count]
    return groups

@lru_cache(maxsize=32)
def load_module_bundle(module_id: str) -> ModuleBundle:
    """
    Load using your naming convention:
      modules/<id>/<id>_questions.txt
      modules/<id>/<id>_answers.txt
      modules/<id>/<id>_notes.txt       (optional)
      modules/<id>/<id>_diagrams.json   (optional)
      modules/<id>/images or diagrams/  (optional assets)
    """
    mdir = Path("modules") / module_id
    if not mdir.exists():
        raise FileNotFoundError(f"Module folder not found: {mdir}")

    q_file = mdir / f"{module_id}_questions.txt"
    a_file = mdir / f"{module_id}_answers.txt"
    n_file = mdir / f"{module_id}_notes.txt"
    d_file = mdir / f"{module_id}_diagrams.json"
    t_file = mdir / "title.txt"  # optional nice title

    q_lines = [ln for ln in _read_lines(q_file) if ln.strip()]
    if not q_lines:
        raise ValueError(f"No questions found in {q_file.name}")
    questions = _parse_qa_lines(q_lines)

    a_lines = [ln for ln in _read_lines(a_file) if ln.strip()]
    answers = _group_answers(a_lines, len(questions))

    notes = [ln for ln in _read_lines(n_file) if ln.strip()]
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
        answers=answers,
        notes=notes,
        diagrams=diagrams,
    )

# ---------- Navigation ----------

def next_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[QuestionPointer]:
    """Advance to next subpart; if none, next question; return None at end."""
    qi, si = ptr.qi, ptr.si
    count = bundle.subparts_count(qi)
    si += 1
    if si < count:
        return QuestionPointer(qi, si)
    qi += 1
    if qi < len(bundle.questions):
        # start at first subpart (0)
        return QuestionPointer(qi, 0)
    return None
