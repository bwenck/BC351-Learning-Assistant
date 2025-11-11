import streamlit as st
from pathlib import Path

# ---------- Page setup ----------
APP_TITLE = "🧬 BC351 Learning Assistant"
st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide")

st.markdown("""
<style>
#root > div:first-child { padding-top: 0.8rem !important; }
.chat-bubble { border-radius: 14px; padding: 12px 14px; margin: 6px 0; max-width: 820px; }
.bubble-tutor { background: #E7F0FD; color: #003366; border: 1px solid #CFE0FB; }
.bubble-student { background: #DFF8E3; color: #084C1E; border: 1px solid #BDEFC8; }
.small { font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Imports from backend ----------
from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, QuestionPointer, next_pointer
from backend.diagram_loader import diagram_for_pointer
from backend.socratic_engine import socratic_followup
from backend.hf_model import init_hf, hf_socratic

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(f"## {APP_TITLE}")
    student_name = st.text_input("Your name", "", placeholder="e.g., Bree")
    
    modules = sorted([p.name for p in Path("modules").iterdir() if p.is_dir()])
    module_id = st.selectbox("Module", modules or ["(none found)"])

    # --- Require name and module before continuing ---
    if not student_name.strip() or module_id in ("", "(no modules found)"):
        st.info("👋 Enter your name and pick a module to begin.")
        st.stop()

    if start_clicked:
        # Reset on restart
        st.session_state.clear()
        st.session_state.state = None
        st.rerun()

    start_clicked = st.button("Start session", type="primary")

# ---------- Load session state only after Start ----------
if "state" not in st.session_state or start_clicked:
    if student_name.strip() and module_id not in ("", "(none found)"):
        st.session_state.state = TutorState.empty(student_name, module_id)
        st.session_state.messages = []

        try:
            bundle = load_module_bundle(module_id)
            st.session_state.state.bundle = bundle
            st.session_state.state.ptr = QuestionPointer(0, 0)
        except Exception as e:
            st.error(f"Module load failed: {e}")
    else:
        st.stop()  # Wait for student + module selection before launching tutor

state: TutorState = st.session_state.state
init_hf()  # free HF inference

# ✅ Define layout columns BEFORE UI draws them
left, right = st.columns([2,1])

# ---------- Left Panel (Chat) ----------
with left:
    # clear input first if needed
    if "clear_box" in st.session_state and st.session_state.clear_box:
        st.session_state.answer_box = ""
        st.session_state.clear_box = False

    # answer input
    ans = st.text_area("Your answer", key="answer_box", placeholder="Type your response…")
    submit = st.button("Submit answer")
    bonus = st.button("Bonus (optional)", disabled=not state.bonus_ok())

    # chat display
    for role, msg in st.session_state.messages:
        cls = "bubble-tutor" if role=="tutor" else "bubble-student"
        who = "🧠 Tutor" if role=="tutor" else f"🟢 {state.student}"
        st.markdown(
            f"<div class='chat-bubble {cls}'><b>{who}</b><br>{msg}</div>",
            unsafe_allow_html=True
        )

# ---------- Right Panel ----------
with right:
    st.subheader("Diagram / Info")
    diag = diagram_for_pointer(state.bundle, state.ptr)
    if diag:
        st.image(f"modules/{state.bundle.module_id}/diagrams/{diag['image']}")
        st.write(diag.get("prompt", "Consider this figure"))

# ---------- Follow-up logic ----------
def tutor_followup(user_text):
    context = state.bundle.context_snips_for(state.ptr)
    question = state.current_question_text()

    socq = socratic_followup(
        module_id=state.bundle.module_id,
        question=question,
        student_answer=user_text,
        context_snips=context,
        student_name=state.student
    )

    follow = hf_socratic(prompt=socq)
    if not follow or "?" not in follow:
        follow = "What biological control normally prevents that?"

    st.session_state.messages.append(("tutor", follow))

# ---------- Submit click ----------
if submit and ans.strip():
    st.session_state.messages.append(("student", ans.strip()))

    # Mark box to clear next run
    st.session_state.clear_box = True

    tutor_followup(ans.strip())

    nxt = next_pointer(state.bundle, state.ptr)
    if nxt:
        state.ptr = nxt
    else:
        st.session_state.messages.append(("tutor", "✅ Module complete! 🎉"))
        st.stop()

# ---------- Bonus ----------
if bonus:
    bq = state.bundle.bonus_question()
    if bq:
        st.session_state.messages.append(("tutor", f"**Bonus question:** {bq}"))
    else:
        st.session_state.messages.append(("tutor", "No bonus question yet."))
