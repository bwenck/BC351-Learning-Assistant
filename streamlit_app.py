import streamlit as st
from pathlib import Path

# backend imports
from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, next_pointer, QuestionPointer
from backend.diagram_loader import diagram_for_pointer
from backend.socratic_engine import socratic_followup
from backend.hf_model import init_hf, hf_socratic


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🧬 BC351 Learning Assistant",
    page_icon="🧬",
    layout="wide"
)


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


# ✅ Encouragement detector for “I don't know”
def is_uncertain(text: str) -> bool:
    t = (text or "").lower()
    triggers = ["i don't know", "idk", "not sure", "no idea", "unsure", "confused", "don't understand", "stuck"]
    return any(x in t for x in triggers)


# ✅ global model init (loaded once per session, not each turn)
if "llm" not in st.session_state:
    st.session_state.llm = init_hf()


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
    if "answer_box" not in st.session_state:
        st.session_state.answer_box = ""

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


    # ---------- Handle SUBMIT ----------
    if submit and ans.strip():

        st.session_state.messages.append(("student", ans.strip()))

        # ✅ If student expresses uncertainty
        if is_uncertain(ans):
            st.session_state.messages.append(
                ("tutor",
                 "That's totally okay — this concept can be tricky. 🧠💭\n"
                 "Think about the molecular checkpoint or regulator involved.\n\n"
                 "If you'd like, you can click **Skip / Next Question ⏭️** at any time."
                 )
            )
            st.session_state.clear_box = True
            st.rerun()

        # ✅ get Socratic follow-up from answer file + model
        question_index = state.ptr.qi
        notes_context = "\n".join(state.bundle.notes)

        follow = hf_socratic(
            st.session_state.llm,
            module_id,
            question_index,
            ans.strip(),
            notes_context
        )

        st.session_state.messages.append(("tutor", follow))

        st.session_state.clear_box = True
        st.rerun()

    # reset input box AFTER render
    if st.session_state.get("clear_box", False):
        st.session_state.answer_box = ""
        st.session_state.clear_box = False
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
