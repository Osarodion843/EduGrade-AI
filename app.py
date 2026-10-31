"""EduGrade AI – Streamlit frontend.

Paper-to-digital grade assistant for overburdened teachers.
Supports Objective (binary: full marks or zero) and Theory (partial credit)
exam types with per-question marks and teacher answer-key reference.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image

from gemma_helper import GemmaHelper, get_helper

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EduGrade AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result: Optional[dict] = None
if "evaluating" not in st.session_state:
    st.session_state.evaluating = False
if "error" not in st.session_state:
    st.session_state.error: Optional[str] = None
if "teacher_images" not in st.session_state:
    st.session_state.teacher_images: list[Image.Image] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def api_configured() -> bool:
    """Return True when a real (non-placeholder) Gemma API key is present."""
    try:
        get_helper()
        return True
    except ValueError:
        return False


def reset_state() -> None:
    st.session_state.result = None
    st.session_state.error = None


def parse_question_marks(
    num_questions: int, marks_input: str
) -> List[Dict[str, Any]]:
    """Parse the marks-per-question input into a list of dicts.

    Accepts either a single number (applied to all questions) or a
    comma-separated list (one value per question).
    """
    marks_input = marks_input.strip()
    if not marks_input:
        # Default: 1 mark per question
        return [
            {"question_number": i + 1, "marks": 1.0}
            for i in range(num_questions)
        ]

    # Try comma-separated list first
    parts = [p.strip() for p in marks_input.split(",") if p.strip()]
    if len(parts) == num_questions:
        try:
            return [
                {"question_number": i + 1, "marks": float(parts[i])}
                for i in range(num_questions)
            ]
        except ValueError:
            pass

    # Fallback: single value applied to all questions
    try:
        single_mark = float(marks_input)
        return [
            {"question_number": i + 1, "marks": single_mark}
            for i in range(num_questions)
        ]
    except ValueError:
        # Last resort: 1 mark per question
        return [
            {"question_number": i + 1, "marks": 1.0}
            for i in range(num_questions)
        ]


def init_question_marks(num_questions: int) -> None:
    """Initialise per-question marks in session state if not present."""
    if "question_marks_list" not in st.session_state:
        st.session_state.question_marks_list = [
            {"question_number": i + 1, "marks": 1.0}
            for i in range(num_questions)
        ]
    else:
        # Adjust list length to match num_questions
        current = st.session_state.question_marks_list
        if len(current) < num_questions:
            for i in range(len(current), num_questions):
                current.append(
                    {"question_number": i + 1, "marks": 1.0}
                )
        elif len(current) > num_questions:
            st.session_state.question_marks_list = current[:num_questions]
            # Re-number
            for i, qm in enumerate(st.session_state.question_marks_list):
                qm["question_number"] = i + 1


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Setup")

    # API status indicator
    if api_configured():
        st.success("✅ Gemma API key configured")
    else:
        st.error(
            "❌ Gemma API key not configured. "
            "Add a real key to `.env` (GEMMA_API_KEY=...)."
        )

    st.divider()

    subject = st.text_input("Subject", placeholder="e.g. Mathematics")
    topic = st.text_input("Topic", placeholder="e.g. Algebra - Linear Equations")

    # Exam type selector
    exam_type = st.radio(
        "Exam Type",
        options=["objective", "theory"],
        format_func=lambda x: "Objective (binary)" if x == "objective" else "Theory (partial credit)",
        help=(
            "Objective: correct = full marks, incorrect = zero (no partial credit).\n"
            "Theory: AI awards partial credit based on closeness to marking guide."
        ),
    )

    st.divider()

    # Question configuration
    st.subheader("📋 Question Configuration")
    num_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=100,
        value=5,
        step=1,
        on_change=lambda: init_question_marks(
            st.session_state.get("_num_questions", num_questions)
        )
        if "_num_questions" in st.session_state
        else None,
    )

    # Sync session state with the widget value
    st.session_state["_num_questions"] = int(num_questions)
    init_question_marks(int(num_questions))

    st.caption("Set the maximum marks for each question individually:")
    question_marks: List[Dict[str, Any]] = []
    cols_per_row = 3
    marks_list = st.session_state.question_marks_list

    # Render mark inputs in rows of 3 for compactness
    for row_start in range(0, len(marks_list), cols_per_row):
        row_items = marks_list[row_start : row_start + cols_per_row]
        cols = st.columns(len(row_items))
        for col, qm in zip(cols, row_items):
            qn = qm["question_number"]
            with col:
                new_marks = st.number_input(
                    f"Q{qn} marks",
                    min_value=0.0,
                    value=float(qm["marks"]),
                    step=0.5,
                    key=f"q_{qn}_marks",
                )
                qm["marks"] = new_marks
                question_marks.append(
                    {"question_number": qn, "marks": new_marks}
                )

    total_marks = sum(qm.get("marks", 0) for qm in question_marks)
    st.info(f"Total maximum score: {total_marks}")

    # Show the question/marks breakdown
    with st.expander("View question marks breakdown", expanded=False):
        for qm in question_marks:
            st.write(f"Q{qm['question_number']}: {qm['marks']} mark(s)")

    st.divider()

    rubric = st.text_area(
        "Marking Rubric / Instructions",
        height=220,
        placeholder=(
            "Describe how each question should be marked.\n\n"
            "Objective example:\n"
            "Q1: What is the capital of Nigeria? Answer: Abuja.\n"
            "Q2: 5 + 7 = ? Answer: 12.\n\n"
            "Theory example:\n"
            "Q1: Explain photosynthesis. Award full marks if the student "
            "mentions light energy, chlorophyll, and CO2.\n"
            "Q2: Discuss the causes of climate change. Mark based on depth "
            "and accuracy.\n"
        ),
    )

    st.divider()

    # Teacher answer key — now REQUIRED
    st.subheader("📚 Teacher Answer Key / Marking Guide (Required)")
    st.caption(
        "Upload your own completed answer sheet image(s). The AI will grade "
        "student papers against these as the authoritative reference."
    )
    teacher_uploads = st.file_uploader(
        "Upload teacher answer sheet(s) (JPEG/PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        on_change=reset_state,
    )

    # Convert uploaded files to PIL images and store in session state
    if teacher_uploads:
        new_images: list[Image.Image] = []
        for uploaded_file in teacher_uploads:
            try:
                img = Image.open(uploaded_file).convert("RGB")
                new_images.append(img)
            except Exception:
                pass
        st.session_state.teacher_images = new_images
    else:
        st.session_state.teacher_images = []

    if st.session_state.teacher_images:
        st.success(
            f"✅ {len(st.session_state.teacher_images)} teacher answer key "
            "image(s) loaded."
        )
    else:
        st.warning(
            "⚠️ Please upload at least one teacher answer key image before "
            "evaluating."
        )

    st.divider()
    st.caption("EduGrade AI • Open source for Hacktoberfest")

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.title("📝 EduGrade AI")
st.caption(
    "Paper-to-digital grade assistant. Upload a handwritten answer sheet and "
    "get a grade + feedback in seconds."
)

uploaded = st.file_uploader(
    "Upload student answer sheet (JPEG/PNG)",
    type=["jpg", "jpeg", "png"],
    on_change=reset_state,
)

# Determine if the evaluate button should be disabled
can_evaluate = (
    uploaded is not None
    and rubric.strip()
    and api_configured()
    and len(st.session_state.teacher_images) > 0
)

col_eval, col_space = st.columns([1, 5])
with col_eval:
    evaluate = st.button(
        "Evaluate Paper",
        type="primary",
        disabled=not can_evaluate,
        help=(
            "Requires: student image, marking rubric, configured API key, "
            "and at least one teacher answer key image."
        ),
    )

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

if evaluate:
    st.session_state.evaluating = True
    st.session_state.error = None
    try:
        image = Image.open(uploaded).convert("RGB")
        helper = get_helper()
        result = helper.evaluate_paper(
            image=image,
            topic=topic or "(not specified)",
            rubric=rubric,
            exam_type=exam_type,
            question_marks=question_marks,
            teacher_images=st.session_state.teacher_images or None,
            max_score=total_marks,
        )
        st.session_state.result = result
    except Exception as exc:  # noqa: BLE001 - surface any error to the user
        st.session_state.error = str(exc)
    finally:
        st.session_state.evaluating = False

# ---------------------------------------------------------------------------
# Results / error display
# ---------------------------------------------------------------------------

if st.session_state.error:
    st.error(f"Evaluation failed: {st.session_state.error}")
    st.info(
        "Tips: verify your GEMMA_API_KEY in `.env`, ensure you have internet "
        "access, and try a clearer image of the answer sheet."
    )

if st.session_state.result:
    result = st.session_state.result

    st.divider()
    st.subheader("📊 Grading Result")

    # Metric cards
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Score", f"{result.get('total_score', 0)}")
    with m2:
        st.metric("Max Score", f"{result.get('max_score', total_marks)}")
    with m3:
        max_s = result.get("max_score", total_marks) or 1
        pct = (result.get("total_score", 0) / max_s) * 100 if max_s else 0
        st.metric("Percentage", f"{pct:.0f}%")

    st.divider()

    tab_extracted, tab_breakdown, tab_feedback = st.tabs(
        ["Extracted Text", "Detailed Breakdown", "Student Feedback"]
    )

    with tab_extracted:
        st.write("**Transcribed answer:**")
        st.write(result.get("extracted_text", "_(none)_"))

    with tab_breakdown:
        st.write(f"**Exam Type:** {result.get('exam_type', 'theory').title()}")
        st.write("**Per-Question Breakdown:**")

        breakdown = result.get("question_breakdown", []) or []
        if breakdown:
            for q in breakdown:
                qn = q.get("question_number", "?")
                marks_awarded = q.get("marks_awarded", 0)
                max_marks = q.get("max_marks", 0)

                # Status indicator based on exam type
                if result.get("exam_type") == "objective":
                    is_correct = q.get("is_correct", False)
                    status = "✅ Correct" if is_correct else "❌ Incorrect"
                else:
                    closeness = q.get("closeness", "")
                    status_map = {
                        "exact": "✅ Exact",
                        "close": "🟡 Close",
                        "partial": "🟠 Partial",
                        "incorrect": "❌ Incorrect",
                        "off-topic": "🔴 Off-topic",
                    }
                    status = status_map.get(closeness, f"• {closeness}")

                with st.container():
                    col_q, col_marks = st.columns([4, 1])
                    with col_q:
                        st.markdown(
                            f"**Q{qn}** — {status} — "
                            f"**{marks_awarded}/{max_marks} marks**"
                        )
                        student_ans = q.get("student_answer", "")
                        if student_ans:
                            st.caption(f"Student: {student_ans}")
                        ref_ans = q.get("correct_answer") or q.get(
                            "reference_answer", ""
                        )
                        if ref_ans:
                            st.caption(f"Reference: {ref_ans}")
                        q_feedback = q.get("feedback", "")
                        if q_feedback:
                            st.caption(f"Feedback: {q_feedback}")
                    with col_marks:
                        st.metric("Awarded", f"{marks_awarded}")
                    st.divider()
        else:
            st.info("No per-question breakdown returned.")

    with tab_feedback:
        st.write("**Constructive feedback for the student:**")
        st.info(result.get("overall_feedback", "_(none)_"))

    st.divider()

    # Download / copy
    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇️ Download result (JSON)",
        data=result_json,
        file_name="edugrade_result.json",
        mime="application/json",
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "EduGrade AI is open source. Built with Streamlit + Google Gemma. "
    "Contributions welcome via Hacktoberfest."
)
