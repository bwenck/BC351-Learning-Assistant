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
from backend.concept_check import is_uncertain, is_gibberish, load_concept_spec
load_concept_spec.cache_clear()

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
left, right = st.columns([1.5, 1])

# ----- get diagram spec for this question (if any) -----
diag = diagram_for_pointer(state.bundle, state.ptr)
is_diag_mcq = isinstance(diag, dict) and diag.get("type") == "mcq"

with left:
    st.subheader("Session")

    # ---------- Answer Input ----------
    if is_diag_mcq:
        st.markdown("**Diagram question**")
        prompt = (diag.get("prompt") or "").strip()
        if prompt:
            st.write(prompt)

        # unique per question *and subpart*
        # (qi = question index, si = subpart index; si can be None)
        si = state.ptr.si if state.ptr.si is not None else 0
        qkey = f"{module_id}_{state.ptr.qi}_{si}"
        choice_key = f"diag_choice_{qkey}"
        form_key = f"diag_form_{qkey}"

        images_dict = diag.get("images") or {}
        options = list(images_dict.keys())  # ["A","B","C"]

        with st.form(key=form_key):
            choice = st.radio(
                "Choose one:",
                options,
                key=choice_key,
                horizontal=True
            )
            col_submit, col_skip, col_bonus = st.columns([1, 1, 1])
            with col_submit:
                submit_diag = st.form_submit_button("Submit diagram answer ✅", use_container_width=True)
            with col_skip:
                skip = st.form_submit_button("Skip / Next Question ⏭️", use_container_width=True)
            with col_bonus:
                bonus = st.form_submit_button("Bonus (optional)", use_container_width=True)

        # disable text-submit path in diagram mode
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
        choice = None

    # ---------- CHAT DISPLAY ----------
    for role, msg in st.session_state.messages:
        bubble_class = "student" if role == "student" else "tutor"
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg}</div>", unsafe_allow_html=True)

# ---------- Handle DIAGRAM SUBMIT ----------
if submit_diag:
    si = state.ptr.si if state.ptr.si is not None else 0
    qkey = f"{module_id}_{state.ptr.qi}_{si}"
    choice_key = f"diag_choice_{qkey}"
    picked = st.session_state.get(choice_key)

    st.session_state.messages.append(("student", f"[Diagram choice: {picked}]"))

    correct = (diag.get("correct") or "").strip().upper()

    if picked and correct and picked.upper() == correct:
        # ✅ use per-question/per-part correct_msg if provided
        msg = (diag.get("correct_msg") or "✅ Correct! Nice work.").strip()
        st.session_state.messages.append(("tutor", msg))

        nxt = next_pointer(state.bundle, state.ptr)
        if nxt:
            state.ptr = nxt
            st.session_state.messages.append(("tutor", state.bundle.question_text(state.ptr)))
        else:
            st.session_state.messages.append(("tutor", "🎉 You've completed this module!"))

        # clear choice so it doesn't persist
        st.session_state.pop(choice_key, None)

    else:
        # ✅ use per-question/per-part incorrect_msg if provided
        msg = (diag.get("incorrect_msg") or
               "Not quite — try comparing which groups can donate/accept a proton under biological conditions.").strip()
        st.session_state.messages.append(("tutor", msg))

    st.rerun()

# ---------- Handle SUBMIT ----------
if submit and ans.strip():
    # 1️⃣ Log this answer in the chat
    st.session_state.messages.append(("student", ans.strip()))

    # 2️⃣ Uncertainty tracking should use ONLY the latest submission
    uncertain_now = is_uncertain(ans.strip())
    gibberish_now = is_gibberish(ans.strip())

    # Track uncertainty count per (module, question)
    ukey = (module_id, state.ptr.qi)  # qid is 0-based
    if "uncertain_counts" not in st.session_state:
        st.session_state.uncertain_counts = {}
    if "gibberish_counts" not in st.session_state:
        st.session_state.gibberish_counts = {}

    prior_uncertain_count = st.session_state.uncertain_counts.get(ukey, 0)
    prior_gibberish_count = st.session_state.gibberish_counts.get(ukey, 0)
    if uncertain_now:
        st.session_state.uncertain_counts[ukey] = prior_uncertain_count + 1
    if gibberish_now:
        st.session_state.gibberish_counts[ukey] = prior_gibberish_count + 1

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
        part_idx=state.ptr.si,
        stem=(state.bundle.questions[state.ptr.qi].get("q") or ""),
        latest_answer=ans.strip(),
        uncertain_now=uncertain_now,
        uncertain_count=prior_uncertain_count,  # count BEFORE this submission
        gibberish_now=gibberish_now,
        gibberish_count=prior_gibberish_count,
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
        if diag.get("type") == "mcq" and isinstance(diag.get("images"), dict):
            imgs = diag["images"]  # {"A":"...", "B":"...", "C":"..."}

            for label, filename in sorted(imgs.items()):
                st.markdown(f"**{label}**")
                st.image(
                    diagram_image_path(module_id, diag, filename),
                    use_column_width=True
                )
        else:
            # single-image legacy support
            img = diag.get("image")
            if img:
                st.image(diagram_image_path(module_id, diag, img))

        prompt = (diag.get("prompt") or "").strip()
        if prompt:
            st.caption(prompt)

    st.markdown("---")
    st.subheader("Progress")
    st.write(
        f"Q{state.ptr.qi+1} · part {state.ptr.si+1} of {state.bundle.subparts_count(state.ptr.qi)}"
    )

    if bonus:
        bq = state.bundle.bonus_question()
        if bq:
            st.session_state.messages.append(("tutor", f"**Bonus question:** {bq}"))
        else:
            st.session_state.messages.append(("tutor", "No bonus question found."))
        st.rerun()

st.write("You can end the session anytime. Switching modules restarts.")
