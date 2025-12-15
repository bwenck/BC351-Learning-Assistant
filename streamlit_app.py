import streamlit as st
from pathlib import Path
import sys

# ✅ Ensure backend is importable in Streamlit Cloud
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))

# backend imports
from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, next_pointer, QuestionPointer
from backend.diagram_loader import diagram_for_pointer
from backend.socratic_engine import socratic_followup
from backend.concept_check import is_uncertain

#from backend.hf_model import init_hf, hf_socratic


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🧬 BC351 Learning Assistant",
    page_icon="🧬",
    layout="wide"
)

st.warning("🚧 Development Build — features may change")

# -------------------------------------------------------
# Safe reset of the answer box BEFORE rendering widgets
# -------------------------------------------------------
if "clear_box" not in st.session_state:
    st.session_state.clear_box = False

if st.session_state.clear_box:
    st.session_state.answer_box = ""
    st.session_state.clear_box = False

# minimalist CSS
st.markdown("""
<style>
.chat-bubble {
    padding: .7rem .9rem;
    border-radius: .6rem;
    margin-bottom: .3rem;
    max-width: 90%;
}
.student {
    background: #d9fdd3;
    margin-left: auto;
}
.tutor {
    background: #e8e8ff;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ✅ global model init (loaded once per session, not each turn)
#if "llm" not in st.session_state:
    #st.session_state.llm = init_hf()


# ---------- SIDEBAR: name + module ----------
st.sidebar.title("🧬 BC351 Learning Assistant")

student_name = st.sidebar.text_input("Your name")
modules_dir = Path("modules")
module_ids = sorted([p.name for p in modules_dir.iterdir() if p.is_dir()])
module_id = st.sidebar.selectbox("Module", module_ids or ["(no modules)"])

start_clicked = st.sidebar.button("Start / Restart", type="primary")

st.sidebar.markdown("---")
st.sidebar.info("Tip: Your answers aren’t graded — the tutor helps you think deeper.")


# ---------- Require name + module before running tutor ----------
if not student_name or module_id not in module_ids:
    st.info("👋 Enter your name and pick a module to begin.")
    st.stop()


# ---------- START FLOW ----------
if "state" not in st.session_state or start_clicked:
    st.session_state.state = TutorState.empty(student_name, module_id)

    try:
        bundle = load_module_bundle(module_id)
        st.session_state.state.bundle = bundle
        st.session_state.messages = [
            ("tutor", f"Welcome, {student_name}! 👋 You selected **{module_id}**."),
            ("tutor", "First question:"),
            ("tutor", st.session_state.state.current_question_text())
        ]
    except Exception as e:
        st.error(f"Error loading module: {e}")
        st.stop()

    st.session_state.clear_box = True
    st.rerun()

state: TutorState = st.session_state.state

# ---------- LAYOUT ----------
left, right = st.columns([2,1])

with left:

    # ---------- Answer Input Box ----------
    ans = st.text_area(
        "Your answer",
        key="answer_box",
        placeholder="Type and press Submit…"
    )

    submit = st.button("Submit answer ✅")
    skip = st.button("Skip / Next Question ⏭️")
    bonus = st.button("Bonus (optional)")

    # ---------- CHAT DISPLAY ----------
    for role, msg in st.session_state.messages:
        bubble_class = "student" if role == "student" else "tutor"
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg}</div>", unsafe_allow_html=True)

# ---------- Handle SUBMIT ----------
if submit and ans.strip():
    # 1️⃣ Log this answer in the chat
    st.session_state.messages.append(("student", ans.strip()))

    # 2️⃣ Accumulate answer history for THIS question
    key = (module_id, state.ptr.qi)  # (module, question index)
    if "answer_history" not in st.session_state:
        st.session_state.answer_history = {}

    prev = st.session_state.answer_history.get(key, "")
    combined = (prev + " " + ans.strip()).strip()
    st.session_state.answer_history[key] = combined

    # 3️⃣ If the student expresses uncertainty, respond gently
    from backend.concept_check import is_uncertain  # if not already imported at top
    if is_uncertain(ans):
        st.session_state.messages.append(
            (
                "tutor",
                "That's totally okay — this concept can be tricky! 🧠💭\n"
                "Think about how normal cell growth is controlled at the molecular level.\n\n"
                "If you'd like, you can also click **Skip / Next Question ⏭️** to move on."
            )
        )
        # we still go on to ask a concept-based follow-up using combined

    # 4️⃣ Ask ONE concept-based Socratic follow-up using the combined answer text
    follow = socratic_followup(module_id, state.ptr.qi, combined)

    # 🔹 Case 1: uncertainty — encourage, do NOT advance
    if isinstance(follow, dict) and follow.get("type") == "uncertain":
        st.session_state.messages.append(("tutor", follow["message"]))

    # 🔹 Case 2: concepts complete — auto-advance
    elif follow is None:
        nxt = next_pointer(state.bundle, state.ptr)
        if nxt:
            st.session_state.messages.append(
                ("tutor", "Nice work — you've hit the key biochemical ideas for this question 💪.")
            )
            state.ptr = nxt
            st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
        else:
            st.session_state.messages.append(
                ("tutor", "🎉 You've completed this module!")
            )

    # 🔹 Case 3: real Socratic follow-up
    else:
        st.session_state.messages.append(("tutor", follow))

    # 5️⃣ Clear the input box on next rerun
    st.session_state.clear_box = True
    st.rerun()

# ---------- Handle SKIP ----------
if skip:
    nxt = next_pointer(state.bundle, state.ptr)
    if nxt:
        state.ptr = nxt
        st.session_state.messages.append(("tutor", "No worries — let's try the next part 😊"))
        st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
    else:
        st.session_state.messages.append(("tutor", "🎉 You've reached the end of this module!"))
    st.session_state.clear_box = True
    st.rerun()

# ---------- RIGHT PANEL ----------
with right:
    st.subheader("Diagram / Info")
    diag = diagram_for_pointer(state.bundle, state.ptr)
    if diag:
        img = diag.get("image")
        prompt = diag.get("prompt")
        if img:
            st.image(f"modules/{module_id}/diagrams/{img}")
        if prompt:
            st.caption(prompt)

    st.markdown("---")
    st.subheader("Progress")
    st.write(f"Q{state.ptr.qi+1} · part {state.ptr.si+1} of {state.bundle.subparts_count(state.ptr.qi)}")

    # Bonus question
    if bonus:
        bq = state.bundle.bonus_question()
        if bq:
            st.session_state.messages.append(("tutor", f"**Bonus question:** {bq}"))
        else:
            st.session_state.messages.append(("tutor", "No bonus question found."))
        st.rerun()


st.write("You can end the session anytime. Switching modules restarts.")
