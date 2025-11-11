import streamlit as st
from pathlib import Path

from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, next_pointer, QuestionPointer
from backend.diagram_loader import diagram_for_pointer
from backend.socratic_engine import socratic_followup

APP_TITLE = "🧬 BC351 Learning Assistant"

# -------- Streamlit Page Config (must be FIRST) --------
st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide")

# -------- Custom CSS --------
st.markdown("""
<style>
.chat-bubble {
    padding: 14px;
    margin: 6px 0;
    border-radius: 12px;
    line-height: 1.4;
    font-size: 0.95rem;
    max-width: 100%;
}
.bubble-tutor {
    background: #E7F0FD;
    color: #003366;
    border-radius: 14px 14px 14px 4px;
}
.bubble-student {
    background: #DFF8E3;
    color: #084C1E;
    border-radius: 14px 14px 4px 14px;
    text-align: right;
}
.chat-box {
    max-height: 520px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# -------- Sidebar: Student & Module --------
with st.sidebar:
    st.title(APP_TITLE)
    student_name = st.text_input("Your name", placeholder="e.g., Bree")

    modules_dir = Path("modules")
    module_ids = sorted([p.name for p in modules_dir.iterdir() if p.is_dir()]) \
        if modules_dir.exists() else []

    module_id = st.selectbox("Module", module_ids or ["(no modules found)"])

    start_clicked = st.button("Start session")

    if not student_name or module_id == "(no modules found)":
        st.info("👋 Enter your name and pick a module to begin.")
        st.stop()

    if start_clicked:
        st.session_state.clear()
        st.session_state.state = None
        st.rerun()

# -------- Create or load session state --------
if "state" not in st.session_state:
    st.session_state.state = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "answer_box" not in st.session_state:
    st.session_state.answer_box = ""
if "clear_box" not in st.session_state:
    st.session_state.clear_box = False

# -------- Initialize state if empty --------
if st.session_state.state is None:
    bundle = load_module_bundle(module_id)
    ptr = QuestionPointer(0,0)
    st.session_state.state = TutorState.empty(student_name, module_id)
    st.session_state.state.bundle = bundle
    st.session_state.state.ptr = ptr

# Alias for convenience
state = st.session_state.state

# -------- UI Layout --------
left, right = st.columns([0.65, 0.35])

with left:
    st.markdown("## Session")
    st.write(f"**Student:** {state.student}")
    st.write(f"**Module:** {state.bundle.title}")

    # Greeting + first question if no messages
    if not st.session_state.messages:
        st.session_state.messages.append((
            "tutor",
            f"Welcome, {state.student}! 👋\n"
            f"You selected **{state.bundle.title}**.\n\n"
            f"First question:\n{state.bundle.question_text(state.ptr)}"
        ))

    # Chat box
    chat = st.container()
    with chat:
        for role, msg in st.session_state.messages:
            cls = "bubble-tutor" if role == "tutor" else "bubble-student"
            who = "🧠 Tutor" if role == "tutor" else f"🟢 {state.student}"
            st.markdown(f"<div class='chat-bubble {cls}'><b>{who}</b><br>{msg}</div>",
                        unsafe_allow_html=True)

    # --- Clear answer box flag ---
    if st.session_state.clear_box:
        st.session_state.answer_box = ""
        st.session_state.clear_box = False

    # --- Answer input ---
    ans = st.text_area(
        "Your answer",
        key="answer_box",
        placeholder="Type your response…"
    )
    submit = st.button("Submit answer")
    bonus = st.button("Bonus (optional)", disabled=not state.bonus_ok())

    # --- Submission handling ---
    if submit and ans.strip():
        st.session_state.messages.append(("student", ans.strip()))

        # Socratic follow-up
        follow = socratic_followup(
            module_id,
            state.ptr.qi,
            state.bundle.question_text(state.ptr),
            ans.strip(),
            state.bundle,
            state.bundle.context_snips_for(state.ptr),
            student_name
        )
        st.session_state.messages.append(("tutor", follow))

        st.session_state.clear_box = True

    # --- Bonus handling ---
    if bonus:
        bq = state.bundle.bonus_question()
        if bq:
            st.session_state.messages.append(("tutor", f"✨ Bonus challenge:\n{bq}"))
        else:
            st.session_state.messages.append(("tutor", "No bonus question available."))

with right:
    st.markdown("### Diagram / Info")
    diag = diagram_for_pointer(state.bundle, state.ptr)
    if diag:
        img = f"modules/{module_id}/images/{diag['image']}"
        st.image(img, caption=diag.get("prompt", ""), use_column_width=True)
        options = diag.get("options", [])
        if options:
            choice = st.radio("Choose one:", options, key=f"diag_{state.ptr.qi}_{state.ptr.si}")
            if st.button("Submit diagram answer"):
                if choice == diag.get("correct"):
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Try again!")

    st.markdown("### Progress")
    total = len(state.bundle.questions)
    subparts = state.bundle.subparts_count(state.ptr.qi)
    st.write(f"Q{state.ptr.qi+1} · part {state.ptr.si+1} of {subparts}")

    if st.button("Next question"):
        nxt = next_pointer(state.bundle, state.ptr)
        if nxt:
            state.ptr = nxt
            st.session_state.messages.append((
                "tutor",
                state.bundle.question_text(nxt)
            ))
            st.session_state.clear_box = True
            st.rerun()
        else:
            st.success("🎉 Module complete! Great work!")

