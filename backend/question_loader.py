from pathlib import Path
import json

#############################################
# Utility: read file lines safely
#############################################
def _read_lines(path: Path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


#############################################
# Load all module content
#############################################
def load_module(module_id: str):
    """
    Load questions, answers, notes, diagrams for a module folder.
    Module must contain:
      <module_id>_questions.txt
      <module_id>_answers.txt
      <module_id>_notes.txt       (optional)
      <module_id>_diagrams.json   (optional)
    """
    mdir = Path("modules") / module_id

    # File paths based on module_id naming convention
    q_file = mdir / f"{module_id}_questions.txt"
    a_file = mdir / f"{module_id}_answers.txt"
    n_file = mdir / f"{module_id}_notes.txt"
    d_file = mdir / f"{module_id}_diagrams.json"

    # Load content
    q_lines = _read_lines(q_file)
    a_lines = _read_lines(a_file)
    notes = _read_lines(n_file) if n_file.exists() else []
    diagrams = {}

    if d_file.exists():
        with open(d_file, "r", encoding="utf-8") as f:
            diagrams = json.load(f)

    # Safety checks
    if not q_lines:
        print(f"❌ ERROR: No questions found in {q_file}")
        return None

    if not a_lines:
        print(f"⚠️ WARNING: No answers found in {a_file} — tutor will not have solution reference")

    # Package module data
    return {
        "id": module_id,
        "questions": q_lines,
        "answers": a_lines,
        "notes": notes,
        "diagrams": diagrams,
        "path": mdir,
    }
