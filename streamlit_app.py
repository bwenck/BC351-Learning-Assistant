import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple

import streamlit as st
from PIL import Image

APP_TITLE = "🧬 BC351 Learning Assistant"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧬",
    layout="wide"
)
# Add top padding fix
st.markdown("""
<style>
#root > div:first-child { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, QuestionPointer, next_pointer
from backend.diagram_loader import diagram_for_pointer
from backend.socratic_engine import socratic_followup
from backend.hf_model import init_hf, hf_socratic

THEME_CSS = """
<style>
/* layout */
.block-container { padding-top: 1.2rem; }
.chat-bubble { border-radius: 14px; padding: 12px 14px; margin: 6px 0; max-width: 820px; }
.bubble-tutor { background: #E7F0FD; color: #003366; border: 1px solid #CFE0FB; }
.bubble-student { background: #DFF8E3; color: #084C1E; border: 1px solid #BDEFC8; }
.small { font-size: 0.88rem; }
.meta { color: #5b6b7a; font-size: 0.82rem; }
.btn-row button { margin-right: 6px; }
img.diagram {
  max-width: 520px; border-radius: 10px; border: 1px solid #ddd; margin: 6px 0;
}
.chat-scroll { max-height: 560px; overflow-y: auto; padding-right: 8px; }
hr.soft { border:none; border-top:1px solid #eee; margin:10px 0 6px; }
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# --------- Sidebar (student + module) ---------
with st.sidebar:
    st.markdown(f"## {APP_TITLE}")
    student_name = st.text_input("Your name", value="", placeholder="e.g., Bree", key="student_name")
    # modules directory discovery
    modules_dir = Path("modules")
    module_ids = sorted([p.name for p in modules_dir.iterdir() if p.is_dir()])
    module_id = st.selectbox("Module", module_ids or ["(no modules found)"], index=0 if module_ids else 0)
    start_clicked = st.button("Start / Restart", type="primary")
    st.markdown("---")
    st.caption("Tip: your answers aren’t graded here. The tutor only asks thoughtful follow-ups.")
    # DEBUG — verify Streamlit sees your module folders
    st.write("DEBUG — modules folder:", list(Path("modules").glob("*")))
    if module_id != "(no modules found)":
        st.write(f"DEBUG — {module_id} files:", list(Path(f"modules/{module_id}").glob("*")))

# --------- Session state boot ---------
if "state" not in st.session_state or start_clicked:
    st.session_state.state = TutorState.empty(student_name or "Student", module_id or "")
    # Load module bundle (questions, answers, notes, diagrams)
    try:
        bundle = load_module_bundle(module_id)
        st.session_state.state.bundle = bundle
        st.session_state.state.ptr = QuestionPointer(0, 0)  # q0, subpart 0
        st.session_state.messages = []  # chat history for UI
    except Exception as e:
        st.error(f"Could not load module '{module_id}': {e}")

state: TutorState = st.session_state.state

# Initialize HF client (free Inference API)
init_hf()  # reads HF token if provided (optional but recommended)

# --------- Chat window ---------
left, right = st.columns([7, 5])
with left:
    st.markdown("### Session")
    chat = st.container()
    with chat:
        st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
        # Initial greeting and first question
        if not st.session_state.messages:
            st.session_state.messages.append(("tutor",
                f"Welcome, {state.student}! 👋\nYou selected **{state.bundle.title}**.\n\n"
                f"**First question:**\n{state.current_question_text()}"
            ))
        # Render chat
        for role, text in st.session_state.messages:
            cls = "bubble-tutor" if role == "tutor" else "bubble-student"
            who = "🧠 Tutor" if role == "tutor" else f"🟢 {state.student}"
            st.markdown(f'<div class="chat-bubble {cls}"><div class="small"><b>{who}</b></div>{text}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Answer input
    ans = st.text_input("Your answer", value="", placeholder="Type your response and press Enter…", key="answer_box")

    # Button row
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        do_submit = st.button("Submit", use_container_width=True)
    with c2:
        do_next = st.button("Next", use_container_width=True)
    with c3:
        do_bonus = st.button("Bonus (optional)", use_container_width=True, disabled=not state.bonus_ok(), help="Try an optional challenge question")

with right:
    st.markdown("### Diagram / Info")
    diag = diagram_for_pointer(state.bundle, state.ptr)
    if diag:
        # diag: { "image": "image_A.png", "prompt": "Which is amphoteric?", "choices": ["A","B","C"] }
        img_path = Path("modules") / state.bundle.module_id / "images" / diag["image"]
        if img_path.exists():
            st.image(str(img_path), caption=diag.get("prompt","Diagram"), use_column_width=True)
        if diag.get("choices"):
            st.markdown("**Choices:** " + ", ".join(diag["choices"]))

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("#### Progress")
    st.progress(state.progress_fraction(), text=f"{state.progress_label()}")
    st.caption("You can end the session anytime. Switching modules will restart.")

# --------- Actions ---------
def ask_socratic(student_text: str):
    """Generate one Socratic follow-up (or move on if empty)."""
    qtext = state.current_question_text()
    context = state.bundle.context_snips_for(state.ptr)  # small, safe snippets (no answer key)
    followup = hf_socratic(
        prompt=socratic_followup(
            module_id=state.bundle.module_id,
            question=qtext,
            student_answer=student_text,
            context_snips=context,
            student_name=state.student
        )
    )
    # sanitize (already quite constrained)
    if not followup or "?" not in followup:
        followup = "What normally regulates this process in healthy cells?"
    st.session_state.messages.append(("tutor", followup))

if do_submit and ans.strip():
    # append student answer
    st.session_state.messages.append(("student", ans.strip()))
    # clear input (Streamlit trick)
    st.session_state.answer_box = ""
    # generate Socratic question
    ask_socratic(ans.strip())

if do_next:
    # advance pointer; if out of subparts, move to next question
    nxt = next_pointer(state.bundle, state.ptr)
    if nxt is None:
        st.session_state.messages.append(("tutor", "✅ You've completed this module! Want to try a different one?"))
    else:
        state.ptr = nxt
        st.session_state.messages.append(("tutor", f"**Next:**\n{state.current_question_text()}"))

if do_bonus:
    # present optional bonus (simple version: last item in module or a tagged bonus)
    bq = state.bundle.bonus_question()
    if bq:
        st.session_state.messages.append(("tutor", f"**Bonus question (optional):**\n{bq}"))
    else:
        st.session_state.messages.append(("tutor", "No bonus question available for this module yet."))
