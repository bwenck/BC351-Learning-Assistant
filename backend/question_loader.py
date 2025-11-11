from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

@dataclass
class QuestionPointer:
    qi: int  # question index
    si: int  # subpart index

@dataclass
class ModuleBundle:
    module_id: str
    title: str
    questions: List[List[str]]  # list of question -> list of subparts strings
    answers: List[List[str]]    # same structure, not shown to model
    notes: List[str]            # optional extra context
    diagrams: dict              # loaded JSON (per-question mapping)

    @staticmethod
    def empty(module_id: str):
        return ModuleBundle(module_id=module_id, title=module_id, questions=[["(no questions)"]], answers=[[""]], notes=[], diagrams={})

    def question_text(self, ptr: QuestionPointer) -> str:
        if not self.questions: return "(no questions)"
        qi = min(max(ptr.qi, 0), len(self.questions)-1)
        sub = self.questions[qi]
        si = min(max(ptr.si, 0), len(sub)-1)
        qtxt = sub[si]
        prefix = f"{qi+1}{chr(97+si)}) "
        return prefix + qtxt

    def subparts_count(self, qi: int) -> int:
        if qi < 0 or qi >= len(self.questions): return 1
        return max(1, len(self.questions[qi]))

    def context_snips_for(self, ptr: QuestionPointer, k: int = 3) -> List[str]:
        # take nearby Qs as small context (never answers)
        snips = []
        for offset in range(-1, 2):
            idx = ptr.qi + offset
            if 0 <= idx < len(self.questions):
                snips.append(" ".join(self.questions[idx])[:160])
        return snips

    def bonus_question(self) -> Optional[str]:
        # optional: place a "bonus" key in diagrams.json or notes last line starting with "BONUS:"
        b = self.diagrams.get("bonus_question")
        if isinstance(b, str) and b.strip():
            return b.strip()
        for line in reversed(self.notes):
            if line.strip().lower().startswith("bonus:"):
                return line.split(":",1)[1].strip()
        return None

def _read_lines(p: Path) -> List[str]:
    if not p.exists(): return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]

def _parse_questions(lines: List[str]) -> List[List[str]]:
    # Parse numbered questions, collect subparts (a), (b)...
    groups: List[List[str]] = []
    current: List[str] = []
    for ln in lines:
        if ln[:2].isdigit() or (len(ln) > 1 and ln[0].isdigit() and ln[1] == "."):
            if current: groups.append(current); current = []
            current = [ln.lstrip("0123456789). ").strip()]
        elif ln.lower().startswith(tuple([f"{chr(97+i)})" for i in range(10)])):
            if not current: current = [""]
            current.append(ln[2:].strip())
        else:
            # continuation line: append to last subpart
            if not current: current = [ln]
            else:
                current[-1] = (current[-1] + " " + ln).strip()
    if current: groups.append(current)
    # ensure each has at least one subpart
    return [g if g else ["(empty)"] for g in groups]

def load_module_bundle(module_id: str) -> ModuleBundle:
    mdir = Path("modules") / module_id
    if not mdir.exists(): raise FileNotFoundError(f"{mdir} not found")

    q_lines = _read_lines(mdir / "questions.txt")
    a_lines = _read_lines(mdir / "answers.txt")
    notes = _read_lines(mdir / "notes.txt") if (mdir / "notes.txt").exists() else []

    questions = _parse_questions(q_lines)
    answers = _parse_questions(a_lines) if a_lines else [[""] for _ in questions]

    diagrams = {}
    dj = mdir / "diagrams.json"
    if dj.exists():
        try:
            diagrams = json.loads(dj.read_text(encoding="utf-8"))
        except Exception:
            diagrams = {}

    title = (mdir / "title.txt").read_text(encoding="utf-8").strip() if (mdir / "title.txt").exists() else module_id
    return ModuleBundle(module_id=module_id, title=title, questions=questions, answers=answers, notes=notes, diagrams=diagrams)

def next_pointer(bundle: ModuleBundle, ptr: QuestionPointer) -> Optional[QuestionPointer]:
    qi, si = ptr.qi, ptr.si + 1
    if si < bundle.subparts_count(qi):
        return QuestionPointer(qi, si)
    qi += 1
    if qi < len(bundle.questions):
        return QuestionPointer(qi, 0)
    return None
