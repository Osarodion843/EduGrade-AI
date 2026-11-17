"""EduGrade AI – Streamlit frontend.

Paper-to-digital grade assistant for overburdened teachers.
Supports Objective and Theory exam types with per-question marks,
teacher answer-key reference, dynamic light/dark theme, camera capture,
split-screen grading, and per-student PDF report export.
"""

from __future__ import annotations

import html
import json
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image

from gemma_helper import get_helper
from theme import inject_theme_css, theme_toggle_button

try:
    from pdf_report import generate_student_report_pdf, letter_grade, report_filename

    PDF_AVAILABLE = True
except ImportError:  # fpdf2 not installed
    PDF_AVAILABLE = False

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EduGrade AI",
    page_icon=":material/edit_note:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def api_configured() -> bool:
    try:
        get_helper()
        return True
    except ValueError:
        return False


def reset_state() -> None:
    st.session_state.result = None
    st.session_state.error = None


def start_new_paper() -> None:
    """Clear the current result and the student-specific inputs."""
    reset_state()
    st.session_state.student_image = None
    st.session_state.capture_nonce += 1  # gives the uploaders fresh keys -> cleared
    for key in ("student_name", "student_id"):
        st.session_state[key] = ""


def init_question_marks(num_questions: int) -> None:
    current = st.session_state.question_marks_list
    if len(current) < num_questions:
        for i in range(len(current), num_questions):
            current.append({"question_number": i + 1, "marks": 1.0})
    elif len(current) > num_questions:
        st.session_state.question_marks_list = current[:num_questions]


def fmt_num(value: Any) -> str:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def esc(value: Any) -> str:
    """Escape model output before putting it inside raw HTML."""
    return html.escape(str(value or "")).replace("\n", "<br>")


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

_DEFAULTS: Dict[str, Any] = {
    "theme": "light",
    "result": None,
    "error": None,
    "teacher_images": [],
    "student_image": None,
    "graded_history": [],
    "capture_nonce": 0,
    "graded_student": {"name": "", "id": ""},
    "question_marks_list": [{"question_number": i + 1, "marks": 1.0} for i in range(5)],
}
for _key, _value in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

inject_theme_css(st.session_state.theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="edu-card-header">Setup</div>', unsafe_allow_html=True)

    theme_toggle_button()
    st.divider()

    if api_configured():
        st.markdown('<span class="edu-badge edu-badge-success">Gemma API configured</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="edu-badge edu-badge-danger">Gemma API not configured</span>', unsafe_allow_html=True)
        st.caption("Add a real key to .env (GEMMA_API_KEY=...) and restart the app.")

    st.divider()

    st.text_input("Subject", placeholder="e.g. Mathematics", key="subject")
    st.text_input("Class", placeholder="e.g. JSS 2B", key="class_name")
    st.text_input("Topic", placeholder="e.g. Algebra - Linear Equations", key="topic")

    exam_type = st.radio(
        "Exam type",
        options=["objective", "theory"],
        format_func=lambda x: "Objective (binary)" if x == "objective" else "Theory (partial credit)",
        help="Objective: correct = full marks, incorrect = zero. Theory: partial credit allowed.",
        on_change=reset_state,
    )

    st.divider()

    st.markdown('<div class="edu-card-header">Question configuration</div>', unsafe_allow_html=True)
    num_questions = st.number_input(
        "Number of questions", min_value=1, max_value=100,
        value=len(st.session_state.question_marks_list), step=1,
    )
    init_question_marks(int(num_questions))

    st.caption("Set the maximum marks for each question individually:")
    question_marks: List[Dict[str, Any]] = []
    cols_per_row = 3
    marks_list = st.session_state.question_marks_list

    for row_start in range(0, len(marks_list), cols_per_row):
        row_items = marks_list[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, qm in zip(cols, row_items):
            qn = qm["question_number"]
            with col:
                new_marks = st.number_input(f"Q{qn} marks", min_value=0.0, value=float(qm["marks"]), step=0.5, key=f"q_{qn}_marks")
                qm["marks"] = new_marks
                question_marks.append({"question_number": qn, "marks": new_marks})

    total_marks = sum(qm.get("marks", 0) for qm in question_marks)
    st.info(f"Total maximum score: {fmt_num(total_marks)}")

    st.divider()

    st.markdown('<div class="edu-card-header">Marking rubric (optional)</div>', unsafe_allow_html=True)
    st.text_area(
        "Marking rubric / instructions",
        key="rubric",
        height=120,
        placeholder="e.g. Accept equivalent wording. Q3 needs both the formula and the final answer.",
        help="Extra instructions for the grader. The teacher answer key below is the main reference.",
    )

    st.markdown('<div class="edu-card-header">Teacher answer key / marking guide (required)</div>', unsafe_allow_html=True)
    st.caption("Upload your own completed answer sheet image(s). The AI grades student papers against these.")
    teacher_uploads = st.file_uploader(
        "Upload teacher answer sheet(s) (JPEG/PNG)", type=["jpg", "jpeg", "png"],
        accept_multiple_files=True, on_change=reset_state,
    )

    teacher_images = []
    for uploaded_file in teacher_uploads or []:
        try:
            teacher_images.append(Image.open(uploaded_file).convert("RGB"))
        except Exception:  # noqa: BLE001 - skip unreadable files, warn below
            st.warning(f"Could not read {uploaded_file.name}; skipped.")
    st.session_state.teacher_images = teacher_images

    if teacher_images:
        st.markdown(f'<span class="edu-badge edu-badge-success">{len(teacher_images)} teacher key image(s) loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="edu-badge edu-badge-warning">Upload at least one teacher answer key</span>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.markdown('<h1 class="edu-title">EduGrade AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="edu-subtitle">Paper-to-digital grade assistant. Upload a handwritten answer sheet and get a grade + feedback in seconds.</p>', unsafe_allow_html=True)

history = st.session_state.graded_history

if st.session_state.result is None:
    # ---- Session dashboard (real numbers from this session) ----------
    with st.container(border=True):
        st.markdown('<div class="edu-card-header">This session</div>', unsafe_allow_html=True)
        avg_pct = sum(h["pct"] for h in history) / len(history) if history else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Papers graded", len(history))
        c2.metric("Average score", f"{avg_pct:.0f}%" if history else "-")
        c3.metric("Last student", history[-1]["name"] if history else "-")
        if history:
            with st.expander("Graded this session", expanded=False):
                st.dataframe(
                    [{"Student": h["name"], "ID": h["id"], "Score": h["score"], "Percentage": f"{h['pct']:.0f}%"} for h in history],
                    hide_index=True,
                )

    # ---- Student details + capture ------------------------------------
    with st.container(border=True):
        st.markdown('<div class="edu-card-header">Student details</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        d1.text_input("Student name", placeholder="e.g. Chidinma Okafor", key="student_name")
        d2.text_input("Student ID / admission no. (optional)", placeholder="e.g. JSS2/045", key="student_id")

        st.markdown('<div class="edu-card-header">Capture student answer sheet</div>', unsafe_allow_html=True)
        nonce = st.session_state.capture_nonce
        col_cam, col_file = st.columns(2)
        with col_cam:
            camera_img = st.camera_input("Snap a photo of the answer sheet", key=f"camera_{nonce}")
        with col_file:
            uploaded = st.file_uploader("Or upload an image (JPEG/PNG)", type=["jpg", "jpeg", "png"], key=f"upload_{nonce}", on_change=reset_state)

        image_source = camera_img if camera_img is not None else uploaded
        student_img: Optional[Image.Image] = None
        if image_source is not None:
            try:
                student_img = Image.open(image_source).convert("RGB")
                st.image(student_img, caption="Student answer sheet preview", width="stretch")
            except Exception:  # noqa: BLE001
                st.error("That file could not be read as an image. Please try another photo.")

        missing = []
        if student_img is None:
            missing.append("a student answer sheet")
        if not st.session_state.teacher_images:
            missing.append("a teacher answer key (sidebar)")
        if not api_configured():
            missing.append("a Gemma API key in .env")
        if missing:
            st.caption("To evaluate, add " + ", ".join(missing) + ".")

        if st.session_state.error:
            st.error(f"Evaluation failed: {st.session_state.error}")
            st.info("Tips: verify your GEMMA_API_KEY in .env, ensure you have internet access, and try a clearer image.")

        if st.button("Evaluate paper", type="primary", disabled=bool(missing), width="stretch"):
            st.session_state.error = None
            try:
                with st.spinner("Reading handwriting and grading..."):
                    result = get_helper().evaluate_paper(
                        image=student_img,
                        topic=st.session_state.topic.strip() or "(not specified)",
                        rubric=st.session_state.rubric.strip() or "Grade strictly against the teacher's answer key.",
                        exam_type=exam_type,
                        question_marks=question_marks,
                        teacher_images=st.session_state.teacher_images,
                        max_score=total_marks,
                    )
            except Exception as exc:  # noqa: BLE001 - shown to the teacher
                st.session_state.error = str(exc)
            else:
                st.session_state.result = result
                st.session_state.student_image = student_img
                # Widget state is dropped once the inputs stop rendering, so keep a copy.
                st.session_state.graded_student = {
                    "name": st.session_state.student_name.strip(),
                    "id": st.session_state.student_id.strip(),
                }
                if not result.get("_parse_error"):
                    max_s = result.get("max_score") or 0
                    history.append({
                        "name": st.session_state.student_name.strip() or f"Student {len(history) + 1}",
                        "id": st.session_state.student_id.strip(),
                        "score": f"{fmt_num(result.get('total_score', 0))}/{fmt_num(max_s)}",
                        "pct": (result.get("total_score", 0) / max_s * 100) if max_s else 0,
                    })
            st.rerun()

else:
    result = st.session_state.result
    student_name = st.session_state.graded_student["name"]
    student_id = st.session_state.graded_student["id"]
    max_s = result.get("max_score") or total_marks
    pct = (result.get("total_score", 0) / max_s) * 100 if max_s else 0

    if result.get("_parse_error"):
        st.warning("The AI's reply could not be read as a grade. Please try again (a clearer photo often helps).")
        with st.expander("Raw model response"):
            st.code(result.get("_raw_response", ""), language=None)

    with st.container(border=True):
        title = f"Grading result - {student_name}" if student_name else "Grading result"
        st.markdown(f'<div class="edu-card-header">{esc(title)}</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Score", f"{fmt_num(result.get('total_score', 0))} / {fmt_num(max_s)}")
        m2.metric("Percentage", f"{pct:.0f}%")
        if PDF_AVAILABLE:
            letter, remark = letter_grade(pct)
            m3.metric("Grade", f"{letter} ({remark})")

        st.divider()

        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown('<div class="edu-card-header">Source image</div>', unsafe_allow_html=True)
            if st.session_state.student_image is not None:
                st.image(st.session_state.student_image, width="stretch")
        with right_col:
            st.markdown('<div class="edu-card-header">AI output</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="edu-feedback-box"><strong>Overall feedback:</strong><br>{esc(result.get("overall_feedback") or "none")}</div>', unsafe_allow_html=True)

        st.divider()

        tab_extracted, tab_breakdown, tab_feedback = st.tabs(["Extracted text", "Detailed breakdown", "Student feedback"])

        with tab_extracted:
            st.markdown("**Transcribed answer:**")
            st.text(result.get("extracted_text") or "none")

        with tab_breakdown:
            st.markdown(f"**Exam type:** {result.get('exam_type', 'theory').title()}")
            breakdown = result.get("question_breakdown", []) or []
            if breakdown:
                for q in breakdown:
                    qn = q.get("question_number", "?")
                    if result.get("exam_type") == "objective":
                        badge = '<span class="edu-badge edu-badge-success">Correct</span>' if q.get("is_correct") else '<span class="edu-badge edu-badge-danger">Incorrect</span>'
                    else:
                        status_map = {"exact": ("edu-badge-success", "Exact"), "close": ("edu-badge-success", "Close"), "partial": ("edu-badge-warning", "Partial"), "incorrect": ("edu-badge-danger", "Incorrect"), "off-topic": ("edu-badge-danger", "Off-topic")}
                        closeness = q.get("closeness", "")
                        badge_class, badge_text = status_map.get(closeness, ("edu-badge-info", closeness or "-"))
                        badge = f'<span class="edu-badge {badge_class}">{esc(badge_text)}</span>'
                    st.markdown(f'<div class="edu-question-row"><span class="edu-q-number">Q{esc(qn)}</span>{badge}<span class="edu-q-status">{fmt_num(q.get("marks_awarded", 0))}/{fmt_num(q.get("max_marks", 0))} marks</span></div>', unsafe_allow_html=True)
                    if q.get("student_answer"):
                        st.caption(f"Student: {q['student_answer']}")
                    ref_ans = q.get("correct_answer") or q.get("reference_answer")
                    if ref_ans:
                        st.caption(f"Reference: {ref_ans}")
                    if q.get("feedback"):
                        st.caption(f"Feedback: {q['feedback']}")
                    st.divider()
            else:
                st.info("No per-question breakdown returned.")

        with tab_feedback:
            st.markdown("**Constructive feedback for the student:**")
            st.markdown(f'<div class="edu-feedback-box">{esc(result.get("overall_feedback") or "none")}</div>', unsafe_allow_html=True)

        st.divider()

        # ---- Export ----------------------------------------------------
        st.markdown('<div class="edu-card-header">Export result</div>', unsafe_allow_html=True)
        include_sheet = st.checkbox("Attach the scanned answer sheet to the PDF", value=True)
        col_dl_pdf, col_dl_json = st.columns(2)
        export = dict(result, student_name=student_name, student_id=student_id,
                      subject=st.session_state.subject.strip(), class_name=st.session_state.class_name.strip())
        with col_dl_pdf:
            if PDF_AVAILABLE:
                try:
                    pdf_bytes = generate_student_report_pdf(
                        result,
                        student_name=student_name,
                        student_id=export["student_id"],
                        class_name=export["class_name"],
                        subject=export["subject"],
                        topic=st.session_state.topic.strip(),
                        max_score=total_marks,
                        answer_sheet=st.session_state.student_image if include_sheet else None,
                    )
                    st.download_button(
                        "Download student report (PDF)", data=pdf_bytes,
                        file_name=report_filename(student_name), mime="application/pdf",
                        type="primary", icon=":material/picture_as_pdf:", width="stretch",
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"PDF generation failed: {exc}")
            else:
                st.button("Download student report (PDF)", disabled=True, help="Install fpdf2: pip install fpdf2", width="stretch")
        with col_dl_json:
            st.download_button(
                "Download result (JSON)", data=json.dumps(export, indent=2, ensure_ascii=False),
                file_name=report_filename(student_name).replace(".pdf", ".json") if PDF_AVAILABLE else "edugrade_result.json",
                mime="application/json", icon=":material/data_object:", width="stretch",
            )

        st.button("Grade another paper", on_click=start_new_paper, icon=":material/restart_alt:", width="stretch")

st.divider()
st.caption("EduGrade AI is open source. Built with Streamlit + Google Gemma. AI grades should be reviewed by the teacher.")
