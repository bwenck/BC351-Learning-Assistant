from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Dict, Any


##########################################
# Data structures the app expects
##########################################

@dataclass
class QuestionPointer:
    q_index: int       # 0-based question index
    sub_index: int     # 0-based part index (-1 = main question only)


@dataclass
class ModuleBundle:
    module_id: str
    questions: List[Dict[str, Any]]     # parsed Q structure
    answers: List[str]
    notes: str


##########################################
# Question Parser — supports a/b/c subparts
##########################################

def parse_questions(raw: str) -> List[Dict[str, Any]]:
    questions = []
    current_q = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        # Detect "1." or "2)" question format
        if line[0].isdigit() and ("." in line[:3] or ")" in line[:3]):
            if current_q:
                questions.append(current_q)
            current_q = {"q": line, "parts": []}
            continue

        # Detect subparts like "a)" or "b."
        if current_q and (
            line.lower().startswith("a)") or line.lower().startswith("b)") or
            line.lower().startswith("c)") or line.lower().startswith("d)")
        ):
            current_q["parts"].append(line)
        else:
            # Append continuation text
            if current_q:
                if current_q["parts"]:
                    current_q["parts"][-1] += " " + line
                else:
                    current_q["q"] += " " + line

    if current_q:
        questions.append(current_q)

    return questions


##########################################
# File loader for module questions/answers
##########################################

@lru_cache(maxsize=8)
def load_module_bundle(module_id: str) -> ModuleBundle:
    """Loads a module's question, answer and notes files."""
    mdir = Path(f"modules/{module_id}")

    q_file = mdir / f"{module_id}_questions.txt"
    a_file = mdir / f"{module_id}_answers.txt"
    n_file = mdir / f"{module_id}_notes.txt"

    if not q_file.exists():
        raise FileNotFoundError(f"❌ Missing question file: {q_file}")

    raw_q = q_file.read_text()
    questions = parse_questions(raw_q)

    if not questions:
        raise ValueError(f"❌ No questions parsed in {q_file}")

    raw_answers = a_file.read_text() if a_file.exists() else ""
    notes = n_file.read_text() if n_file.exists() else ""

    return ModuleBundle(
        module_id=module_id,
        questions=questions,
        answers=raw_answers.splitlines(),
        notes=notes
    )
