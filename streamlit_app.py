import streamlit as st
from pathlib import Path
import sys

# ✅ Ensure backend is importable in Streamlit Cloud
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))

# backend imports
from backend.tutor_state import TutorState
from backend.question_loader import load_module_bundle, next_pointer, QuestionPointer
from backend.diagram_loader import diagram_for_pointer, diagram_image_path

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
    # ----- get diagram spec for this question (if any) -----
    diag = diagram_for_pointer(state.bundle, state.ptr)
    is_diag_mcq = isinstance(diag, dict) and diag.get("type") == "mcq"

    with left:
        # ---------- Answer Input ----------
        if is_diag_mcq:
            st.markdown("**Diagram question**")
            prompt = diag.get("prompt", "").strip()
            if prompt:
                st.write(prompt)

            # radio choice (unique per question)
            qnum = state.ptr.qi + 1
            choice_key = f"diag_choice_{module_id}_{qnum}"
            options = list((diag.get("images") or {}).keys())  # ["A","B","C"]
            if options:
                choice = st.radio("Choose one:", options, key=choice_key, horizontal=True)
            else:
                choice = None
                st.error("Diagram spec has no images/options.")

            col_submit, col_skip, col_bonus = st.columns([1, 1, 1])
            with col_submit:
                submit_diag = st.button("Submit diagram answer ✅", use_container_width=True)
            with col_skip:
                skip = st.button("Skip / Next Question ⏭️", use_container_width=True)
            with col_bonus:
                bonus = st.button("Bonus (optional)", use_container_width=True)

            # (no text box in diagram mode)
            submit = False
            ans = ""
        else:
            ans = st.text_area(
                "Your answer",
                key="answer_box",
                placeholder="Type and press Submit…"
            )
            col_submit, col_skip, col_bonus = st.columns([1, 1, 1])
            with col_submit:
                submit = st.button("Submit answer ✅", use_container_width=True)
            with col_skip:
                skip = st.button("Skip / Next Question ⏭️", use_container_width=True)
            with col_bonus:
                bonus = st.button("Bonus (optional)", use_container_width=True)

            submit_diag = False

    # ---------- CHAT DISPLAY ----------
    for role, msg in st.session_state.messages:
        bubble_class = "student" if role == "student" else "tutor"
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg}</div>", unsafe_allow_html=True)

# ---------- Handle DIAGRAM SUBMIT ----------
if is_diag_mcq and submit_diag:
    qnum = state.ptr.qi + 1
    chosen = st.session_state.get(f"diag_choice_{module_id}_{qnum}")
    correct = (diag.get("correct") or "").strip().upper()

    if chosen and correct and chosen.upper() == correct:
        st.session_state.messages.append(("student", f"[Diagram choice: {chosen}]"))
        st.session_state.messages.append(("tutor", diag.get("correct_msg", "✅ Correct!")))

        # auto-advance
        nxt = next_pointer(state.bundle, state.ptr)
        if nxt:
            state.ptr = nxt
            st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
        else:
            st.session_state.messages.append(("tutor", "🎉 You've completed this module!"))
    else:
        st.session_state.messages.append(("student", f"[Diagram choice: {chosen}]"))
        st.session_state.messages.append(("tutor", diag.get("incorrect_msg", "Not quite — try again.")))

    st.rerun()

# ---------- Handle SUBMIT ----------
if submit and ans.strip():
    # 1️⃣ Log this answer in the chat
    st.session_state.messages.append(("student", ans.strip()))

    # 2️⃣ Uncertainty tracking should use ONLY the latest submission
    uncertain_now = is_uncertain(ans.strip())

    # Track uncertainty count per (module, question)
    ukey = (module_id, state.ptr.qi)  # qid is 0-based
    if "uncertain_counts" not in st.session_state:
        st.session_state.uncertain_counts = {}

    prior_uncertain_count = st.session_state.uncertain_counts.get(ukey, 0)
    if uncertain_now:
        st.session_state.uncertain_counts[ukey] = prior_uncertain_count + 1

    # 3️⃣ Accumulate answer history for THIS question (but DO NOT store uncertainty answers)
    key = (module_id, state.ptr.qi)
    if "answer_history" not in st.session_state:
        st.session_state.answer_history = {}

    prev = st.session_state.answer_history.get(key, "")

    if uncertain_now:
        combined = prev  # keep prior real content only
    else:
        combined = (prev + " " + ans.strip()).strip()
        st.session_state.answer_history[key] = combined

    # 4️⃣ Ask ONE concept-based Socratic follow-up using combined history
    follow = socratic_followup(
        module_id,
        state.ptr.qi,
        combined,
        uncertain_now=uncertain_now,
        uncertain_count=prior_uncertain_count,  # count BEFORE this submission
    )

    # 5️⃣ If concepts complete → auto-advance
    if follow is None:
        st.session_state.messages.append(
            ("tutor", "Nice work — you've hit the key biochemical ideas for this question 💪.")
        )
        nxt = next_pointer(state.bundle, state.ptr)
        if nxt:
            state.ptr = nxt
            st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
        else:
            st.session_state.messages.append(("tutor", "🎉 You've completed this module!"))
    else:
        st.session_state.messages.append(("tutor", follow))

    # 6️⃣ Clear the input box on next rerun
    st.session_state.clear_box = True
    st.rerun()

# ---------- Handle SKIP ----------
if skip:
    nxt = next_pointer(state.bundle, state.ptr)
    if nxt:
        state.ptr = nxt
        st.session_state.messages.append(("tutor", "No problem — we'll move on for now ⏭️"))
        st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
    else:
        st.session_state.messages.append(("tutor", "🎉 You've reached the end of this module!"))
    st.session_state.clear_box = True
    st.rerun()

# ---------- RIGHT PANEL ----------
with right:
    st.subheader("Diagram / Info")
    diag = diagram_for_pointer(state.bundle, state.ptr)
    if isinstance(diag, dict):
        # If MCQ diagram, show A/B/C
        if diag.get("type") == "mcq" and isinstance(diag.get("images"), dict):
            imgs = diag["images"]  # {"A": "...", "B": "...", "C": "..."}
            cols = st.columns(len(imgs))
            for i, (label, filename) in enumerate(sorted(imgs.items())):
                with cols[i]:
                    st.markdown(f"**{label}**")
                    st.image(diagram_image_path(module_id, diag, filename))

                    # Radio + submit controls
                    options = list(sorted(imgs.keys()))  # ["A","B","C"]
                    qkey = f"diag_choice_{module_id}_{state.ptr.qi}"
                    skey = f"diag_submit_{module_id}_{state.ptr.qi}"

                    picked = st.radio("Choose one:", options, key=qkey, horizontal=True)

                    if st.button("Submit diagram answer ✅", key=skey, use_container_width=True):
                        correct = diag.get("correct")  # e.g. "C"
                        if correct and picked == correct:
                            st.session_state.messages.append(("tutor", "✅ Correct — nice. Let’s continue."))

                            nxt = next_pointer(state.bundle, state.ptr)
                            if nxt:
                                state.ptr = nxt
                                st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
                            else:
                                st.session_state.messages.append(("tutor", "🎉 You've completed this module!"))
                            st.rerun()
                        else:
                            st.session_state.messages.append(
                                ("tutor",
                                 "Not quite — try comparing which group can donate/accept H⁺ in an organic context.")
                            )
                            st.rerun()

        else:
            # legacy single-image support (optional)
            img = diag.get("image")
            if img:
                st.image(diagram_image_path(module_id, diag, img))

        prompt = diag.get("prompt")
        if prompt:
            st.caption(prompt)

    st.markdown("---")
    st.subheader("Progress")
    st.write(f"Q{state.ptr.qi+1} · part {state.ptr.si+1} of {state.bundle.subparts_count(state.ptr.qi)}")

    if bonus:
        bq = state.bundle.bonus_question()
        if bq:
            st.session_state.messages.append(("tutor", f"**Bonus question:** {bq}"))
        else:
            st.session_state.messages.append(("tutor", "No bonus question found."))
        st.rerun()

st.write("You can end the session anytime. Switching modules restarts.")
