# backend/tutor_state.py
from dataclasses import dataclass
from typing import Optional
from backend.question_loader import ModuleBundle, QuestionPointer

@dataclass
class TutorState:
    student: str
    module_id: str
    bundle: ModuleBundle
    ptr: QuestionPointer

    @staticmethod
    def empty(student: str, module_id: str):
        # start with a harmless placeholder bundle; app will load the real one
        return TutorState(
            student=student or "Student",
            module_id=module_id,
            bundle=ModuleBundle.empty(),
            ptr=QuestionPointer(0, 0)
        )

    def current_question_text(self) -> str:
        return self.bundle.question_text(self.ptr)

    def bonus_ok(self) -> bool:
        # allow when a bonus exists (keeps button enabled only if there’s one)
        return bool(self.bundle.bonus_question())

    # (Optional) helpers for persistence later:
    def to_dict(self):
        return {
            "student": self.student,
            "module_id": self.module_id,
            "ptr": {"qi": self.ptr.qi, "si": self.ptr.si},
        }

    @staticmethod
    def from_dict(d: dict, bundle: ModuleBundle):
        ptr = QuestionPointer(d["ptr"]["qi"], d["ptr"]["si"])
        return TutorState(d["student"], d["module_id"], bundle, ptr)
