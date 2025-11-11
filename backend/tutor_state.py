from dataclasses import dataclass, field
from typing import Optional, List
from backend.question_loader import ModuleBundle, QuestionPointer

@dataclass
class TutorState:
    student: str
    bundle: ModuleBundle
    ptr: QuestionPointer
    _bonus_ok: bool = True

    @staticmethod
    def empty(student: str, module_id: str):
        return TutorState(student=student or "Student", bundle=ModuleBundle.empty(module_id), ptr=QuestionPointer(0,0))

    def current_question_text(self) -> str:
        return self.bundle.question_text(self.ptr)

    def progress_fraction(self) -> float:
        idx = self.ptr.qi + (self.ptr.si / max(1, self.bundle.subparts_count(self.ptr.qi)))
        total = len(self.bundle.questions)
        return min(1.0, idx / max(1, total))

    def progress_label(self) -> str:
        return f"Q{self.ptr.qi+1} · part {chr(97+self.ptr.si)} of {self.bundle.subparts_count(self.ptr.qi)}"

    def bonus_ok(self) -> bool:
        return self._bonus_ok
