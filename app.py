"""EduGrade AI – Streamlit frontend (Redesigned).

Paper-to-digital grade assistant for overburdened teachers.
Supports Objective and Theory exam types with per-question marks,
teacher answer-key reference, dynamic light/dark theme, camera capture,
split-screen grading, and PDF export.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image

from gemma_helper import GemmaHelper, get_helper

try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EduGrade AI",
    page_icon=":pencil:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme engine
# ---------------------------------------------------------------------------

THEME_CSS_LIGHT = """
<style>
:root {
    --edu-bg-primary: #ffffff;
    --edu-bg-secondary: #f1f5f9;
    --edu-bg-tertiary: #f1f5f9;
    --edu-text-primary: #0f172a;
    --edu-text-secondary: #334155;
    --edu-text-muted: #64748b;
    --edu-accent: #2563eb;
    --edu-accent-hover: #1d4ed8;
    --edu-success: #10b981;
    --edu-success-bg: #d1fae5;
    --edu-warning: #f59e0b;
    --edu-warning-bg: #fef3c7;
    --edu-danger: #ef4444;
    --edu-border: #cbd5e1;
    --edu-card-bg: #ffffff;
    --edu-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
}

/* Force light mode on everything */
.stApp, .stApp * {
    background-color: var(--edu-bg-secondary) !important;
    color: var(--edu-text-primary) !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
.stSidebar,
.stSidebar * {
    background-color: var(--edu-bg-tertiary) !important;
    color: var(--edu-text-primary) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--edu-text-primary) !important;
}

.edu-title {
    color: var(--edu-text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
}

.edu-subtitle {
    color: var(--edu-text-secondary);
}

.edu-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    margin-bottom: 1rem;
}

.edu-card-header {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--edu-text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.edu-metric-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.edu-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--edu-accent);
}

.edu-metric-label {
    font-size: 0.875rem;
    color: var(--edu-text-secondary);
    margin-top: 0.25rem;
}

.edu-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.edu-badge-success {
    background: var(--edu-success-bg);
    color: var(--edu-success);
    border: 1px solid #a7f3d0;
}

.edu-badge-warning {
    background: var(--edu-warning-bg);
    color: #92400e;
    border: 1px solid #fcd34d;
}

.edu-badge-danger {
    background: #fee2e2;
    color: var(--edu-danger);
    border: 1px solid #fecaca;
}

.edu-badge-info {
    background: #dbeafe;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

.edu-progress-tracker {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}

.edu-progress-label {
    font-size: 0.875rem;
    color: var(--edu-text-secondary);
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
}

.edu-split-panel {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.edu-feedback-box {
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-left: 4px solid var(--edu-accent);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    color: var(--edu-text-primary);
    box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.05);
}

.edu-question-row {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
}

.edu-q-number {
    font-weight: 700;
    color: var(--edu-accent);
    min-width: 2rem;
}

.edu-q-status {
    font-size: 0.75rem;
    font-weight: 600;
}

/* Input fields - force dark text on light background */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}

input::placeholder, textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

/* Labels */
label, .stLabel, [data-testid="stWidgetLabel"] p {
    color: #0f172a !important;
    font-weight: 500 !important;
}

/* Buttons */
.stButton > button {
    background: var(--edu-accent);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1rem;
    width: 100%;
}

.stButton > button:hover {
    background: var(--edu-accent-hover);
}

/* Metrics */
.stMetric {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    border-radius: 10px;
    padding: 1rem;
    box-shadow: var(--edu-shadow);
}

.stMetric > div {
    color: var(--edu-text-primary);
}

.stMetric [data-testid="stMetricLabel"] {
    color: var(--edu-text-secondary) !important;
}

.stMetric [data-testid="stMetricValue"] {
    color: var(--edu-accent) !important;
}

/* Alerts */
.stAlert {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    color: var(--edu-text-primary);
}

/* File uploader */
.stFileUploader > div {
    background: var(--edu-bg-tertiary);
    border: 2px dashed var(--edu-border);
    border-radius: 10px;
}

.stFileUploader > div:hover {
    border-color: var(--edu-accent);
}

/* Radio buttons */
.stRadio > div {
    color: var(--edu-text-primary);
}

.stRadio label {
    color: var(--edu-text-primary) !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--edu-bg-tertiary) !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--edu-text-secondary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--edu-accent) !important;
}

/* Divider */
hr, .stDivider {
    border-color: var(--edu-border) !important;
}

/* Caption text */
.stCaption, .stCaption p {
    color: var(--edu-text-secondary) !important;
}

/* Info/warning/error boxes */
.stAlert > div {
    color: var(--edu-text-primary) !important;
}
</style>
"""

THEME_CSS_DARK = """
<style>
:root {
    --edu-bg-primary: #0f172a;
    --edu-bg-secondary: #020617;
    --edu-bg-tertiary: #1e293b;
    --edu-text-primary: #f1f5f9;
    --edu-text-secondary: #94a3b8;
    --edu-text-muted: #64748b;
    --edu-accent: #60a5fa;
    --edu-accent-hover: #3b82f6;
    --edu-success: #34d399;
    --edu-success-bg: #064e3b;
    --edu-warning: #fbbf24;
    --edu-warning-bg: #451a03;
    --edu-danger: #f87171;
    --edu-border: #334155;
    --edu-card-bg: #1e293b;
    --edu-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.2);
}

.stApp {
    background-color: var(--edu-bg-secondary);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--edu-text-primary) !important;
}

.edu-title {
    color: var(--edu-text-primary);
    font-weight: 700;
    letter-spacing: -0.025em;
}

.edu-subtitle {
    color: var(--edu-text-secondary);
}

.edu-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    margin-bottom: 1rem;
}

.edu-card-header {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--edu-text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.edu-metric-card {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

.edu-metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--edu-accent);
}

.edu-metric-label {
    font-size: 0.875rem;
    color: var(--edu-text-muted);
    margin-top: 0.25rem;
}

.edu-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.edu-badge-success {
    background: var(--edu-success-bg);
    color: var(--edu-success);
    border: 1px solid #065f46;
}

.edu-badge-warning {
    background: var(--edu-warning-bg);
    color: #fbbf24;
    border: 1px solid #b45309;
}

.edu-badge-danger {
    background: #450a0a;
    color: var(--edu-danger);
    border: 1px solid #7f1d1d;
}

.edu-badge-info {
    background: #1e3a8a;
    color: #93c5fd;
    border: 1px solid #1e40af;
}

.edu-progress-tracker {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}

.edu-progress-label {
    font-size: 0.875rem;
    color: var(--edu-text-secondary);
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
}

.edu-split-panel {
    background: #ffffff;
    border: 2px solid #94a3b8;
    border-radius: 10px;
    padding: 1rem;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.edu-feedback-box {
    background: var(--edu-bg-tertiary);
    border: 1px solid var(--edu-border);
    border-left: 4px solid var(--edu-accent);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    color: var(--edu-text-primary);
}

.edu-question-row {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
}

.edu-q-number {
    font-weight: 700;
    color: var(--edu-accent);
    min-width: 2rem;
}

.edu-q-status {
    font-size: 0.75rem;
    font-weight: 600;
}

input, textarea, select {
    background-color: var(--edu-bg-primary) !important;
    color: var(--edu-text-primary) !important;
    border: 1px solid var(--edu-border) !important;
}

.stButton > button {
    background: var(--edu-accent);
    color: #0f172a;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1rem;
    width: 100%;
}

.stButton > button:hover {
    background: var(--edu-accent-hover);
}

.stMetric {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    border-radius: 10px;
    padding: 1rem;
    box-shadow: var(--edu-shadow);
}

.stMetric > div {
    color: var(--edu-text-primary);
}

.stAlert {
    background: var(--edu-card-bg);
    border: 1px solid var(--edu-border);
    color: var(--edu-text-primary);
}

.stFileUploader > div {
    background: var(--edu-bg-tertiary);
    border: 2px dashed var(--edu-border);
    border-radius: 10px;
}

.stFileUploader > div:hover {
    border-color: var(--edu-accent);
}

/* Input fields - force light text on dark background */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background-color: var(--edu-bg-primary) !important;
    color: var(--edu-text-primary) !important;
    border: 1px solid var(--edu-border) !important;
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* Labels */
label, .stLabel, [data-testid="stWidgetLabel"] p {
    color: var(--edu-text-primary) !important;
    font-weight: 500 !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: var(--edu-bg-primary) !important;
    color: var(--edu-text-primary) !important;
    border: 1px solid var(--edu-border) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--edu-bg-tertiary) !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--edu-text-secondary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--edu-accent) !important;
}

/* Divider */
hr, .stDivider {
    border-color: var(--edu-border) !important;
}

/* Caption text */
.stCaption, .stCaption p {
    color: var(--edu-text-secondary) !important;
}

/* Info/warning/error boxes */
.stAlert > div {
    color: var(--edu-text-primary) !important;
}
</style>
"""


def inject_theme_css(theme: str) -> None:
    if theme == "dark":
        st.markdown(THEME_CSS_DARK, unsafe_allow_html=True)
    else:
        st.markdown(THEME_CSS_LIGHT, unsafe_allow_html=True)


def theme_toggle_button() -> None:
    current = st.session_state.get("theme", "light")
    label = "Dark Mode" if current == "light" else "Light Mode"
    if st.button(label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "dark" if current == "light" else "light"
        st.rerun()


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


def parse_question_marks(num_questions: int, marks_input: str) -> List[Dict[str, Any]]:
    marks_input = marks_input.strip()
    if not marks_input:
        return [{"question_number": i + 1, "marks": 1.0} for i in range(num_questions)]

    parts = [p.strip() for p in marks_input.split(",") if p.strip()]
    if len(parts) == num_questions:
        try:
            return [{"question_number": i + 1, "marks": float(parts[i])} for i in range(num_questions)]
        except ValueError:
            pass

    try:
        single_mark = float(marks_input)
        return [{"question_number": i + 1, "marks": single_mark} for i in range(num_questions)]
    except ValueError:
        return [{"question_number": i + 1, "marks": 1.0} for i in range(num_questions)]


def init_question_marks(num_questions: int) -> None:
    if "question_marks_list" not in st.session_state:
        st.session_state.question_marks_list = [{"question_number": i + 1, "marks": 1.0} for i in range(num_questions)]
    else:
        current = st.session_state.question_marks_list
        if len(current) < num_questions:
            for i in range(len(current), num_questions):
                current.append({"question_number": i + 1, "marks": 1.0})
        elif len(current) > num_questions:
            st.session_state.question_marks_list = current[:num_questions]
            for i, qm in enumerate(st.session_state.question_marks_list):
                qm["question_number"] = i + 1


def generate_pdf(result: Dict[str, Any], total_marks: float) -> bytes:
    if not FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 is not installed. Run: pip install fpdf2")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "EduGrade AI - Grading Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Topic: {result.get('topic', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Exam Type: {result.get('exam_type', 'theory').title()}", ln=True)
    pdf.cell(0, 8, f"Total Score: {result.get('total_score', 0)} / {result.get('max_score', total_marks)}", ln=True)
    max_s = result.get("max_score", total_marks) or 1
    pct = (result.get("total_score", 0) / max_s) * 100 if max_s else 0
    pdf.cell(0, 8, f"Percentage: {pct:.0f}%", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Per-Question Breakdown", ln=True)
    pdf.set_font("Arial", "", 12)

    breakdown = result.get("question_breakdown", []) or []
    if breakdown:
        for q in breakdown:
            qn = q.get("question_number", "?")
            marks_awarded = q.get("marks_awarded", 0)
            max_marks = q.get("max_marks", 0)
            if result.get("exam_type") == "objective":
                status = "Correct" if q.get("is_correct", False) else "Incorrect"
            else:
                closeness = q.get("closeness", "")
                status_map = {"exact": "Exact", "close": "Close", "partial": "Partial", "incorrect": "Incorrect", "off-topic": "Off-topic"}
                status = status_map.get(closeness, str(closeness))
            pdf.multi_cell(0, 7, f"Q{qn}: {marks_awarded}/{max_marks} marks ({status})\n  Student: {q.get('student_answer', '')}\n  Reference: {q.get('correct_answer') or q.get('reference_answer', '')}\n  Feedback: {q.get('feedback', '')}")
            pdf.ln(2)
    else:
        pdf.cell(0, 8, "No per-question breakdown available.", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Overall Feedback", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, result.get("overall_feedback", ""))

    return pdf.output(dest="S").encode("latin-1")


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "result" not in st.session_state:
    st.session_state.result: Optional[dict] = None
if "evaluating" not in st.session_state:
    st.session_state.evaluating = False
if "error" not in st.session_state:
    st.session_state.error: Optional[str] = None
if "teacher_images" not in st.session_state:
    st.session_state.teacher_images: list = []
if "question_marks_list" not in st.session_state:
    st.session_state.question_marks_list = [{"question_number": i + 1, "marks": 1.0} for i in range(5)]

# ---------------------------------------------------------------------------
# Inject theme CSS
# ---------------------------------------------------------------------------

inject_theme_css(st.session_state.theme)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="edu-card">', unsafe_allow_html=True)
    st.markdown('<div class="edu-card-header">Setup</div>', unsafe_allow_html=True)

    theme_toggle_button()
    st.divider()

    if api_configured():
        st.markdown('<span class="edu-badge edu-badge-success">Gemma API configured</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="edu-badge edu-badge-danger">Gemma API not configured</span>', unsafe_allow_html=True)
        st.caption("Add a real key to .env (GEMMA_API_KEY=...)")

    st.divider()

    subject = st.text_input("Subject", placeholder="e.g. Mathematics")
    topic = st.text_input("Topic", placeholder="e.g. Algebra - Linear Equations")

    exam_type = st.radio(
        "Exam Type",
        options=["objective", "theory"],
        format_func=lambda x: "Objective (binary)" if x == "objective" else "Theory (partial credit)",
        help="Objective: correct = full marks, incorrect = zero. Theory: partial credit allowed.",
    )

    st.divider()

    st.markdown('<div class="edu-card-header">Question Configuration</div>', unsafe_allow_html=True)
    num_questions = st.number_input("Number of Questions", min_value=1, max_value=100, value=len(st.session_state.question_marks_list), step=1)
    st.session_state["_num_questions"] = int(num_questions)
    init_question_marks(int(num_questions))

    st.caption("Set the maximum marks for each question individually:")
    question_marks: List[Dict[str, Any]] = []
    cols_per_row = 3
    marks_list = st.session_state.question_marks_list

    for row_start in range(0, len(marks_list), cols_per_row):
        row_items = marks_list[row_start:row_start + cols_per_row]
        cols = st.columns(len(row_items))
        for col, qm in zip(cols, row_items):
            qn = qm["question_number"]
            with col:
                new_marks = st.number_input(f"Q{qn} marks", min_value=0.0, value=float(qm["marks"]), step=0.5, key=f"q_{qn}_marks")
                qm["marks"] = new_marks
                question_marks.append({"question_number": qn, "marks": new_marks})

    total_marks = sum(qm.get("marks", 0) for qm in question_marks)
    st.info(f"Total maximum score: {total_marks}")

    with st.expander("View question marks breakdown", expanded=False):
        for qm in question_marks:
            st.write(f"Q{qm['question_number']}: {qm['marks']} mark(s)")

    st.divider()

    st.markdown('<div class="edu-card-header">Teacher Answer Key / Marking Guide (Required)</div>', unsafe_allow_html=True)
    st.caption("Upload your own completed answer sheet image(s). The AI will grade student papers against these as the authoritative reference.")
    teacher_uploads = st.file_uploader("Upload teacher answer sheet(s) (JPEG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, on_change=reset_state)

    if teacher_uploads:
        new_images = []
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
        st.markdown(f'<span class="edu-badge edu-badge-success">{len(st.session_state.teacher_images)} teacher key image(s) loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="edu-badge edu-badge-warning">Upload at least one teacher answer key</span>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

st.markdown('<h1 class="edu-title">EduGrade AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="edu-subtitle">Paper-to-digital grade assistant. Upload a handwritten answer sheet and get a grade + feedback in seconds.</p>', unsafe_allow_html=True)

if st.session_state.result is None:
    st.markdown('<div class="edu-card">', unsafe_allow_html=True)
    st.markdown('<div class="edu-card-header">Class Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="edu-metric-card"><div class="edu-metric-value">85</div><div class="edu-metric-label">Students in Class</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="edu-metric-card"><div class="edu-metric-value">0</div><div class="edu-metric-label">Graded Today</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="edu-metric-card"><div class="edu-metric-value">2m</div><div class="edu-metric-label">Avg. Grading Time</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="edu-metric-card"><div class="edu-metric-value">15%</div><div class="edu-metric-label">Pending Review</div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="edu-progress-tracker">', unsafe_allow_html=True)
    st.markdown('<div class="edu-progress-label"><span>Batch Analysis</span><span>49 / 85</span></div>', unsafe_allow_html=True)
    st.progress(49 / 85)
    st.caption("49 of 85 papers analysed — 36 remaining in the batch queue.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="edu-card">', unsafe_allow_html=True)
    st.markdown('<div class="edu-card-header">Capture Student Answer Sheet</div>', unsafe_allow_html=True)

    col_cam, col_file = st.columns(2)
    with col_cam:
        camera_img = st.camera_input("Snap a photo of the answer sheet")
    with col_file:
        uploaded = st.file_uploader("Or upload an image (JPEG/PNG)", type=["jpg", "jpeg", "png"], on_change=reset_state)

    image_source = camera_img if camera_img is not None else uploaded

    if image_source is not None:
        img = Image.open(image_source).convert("RGB")
        st.image(img, caption="Student answer sheet preview", use_container_width=True)

    can_evaluate = (
        image_source is not None
        and st.session_state.get("rubric", "").strip()
        and api_configured()
        and len(st.session_state.teacher_images) > 0
    )

    st.button("Evaluate Paper", type="primary", disabled=not can_evaluate, use_container_width=True, key="evaluate_btn")

    if st.session_state.get("evaluate_btn", False) and can_evaluate:
        st.session_state.evaluating = True
        st.session_state.error = None
        try:
            pil_image = Image.open(image_source).convert("RGB")
            helper = get_helper()
            result = helper.evaluate_paper(
                image=pil_image,
                topic=st.session_state.get("topic", "(not specified)"),
                rubric=st.session_state.get("rubric", ""),
                exam_type=exam_type,
                question_marks=question_marks,
                teacher_images=st.session_state.teacher_images or None,
                max_score=total_marks,
            )
            st.session_state.result = result
        except Exception as exc:
            st.session_state.error = str(exc)
        finally:
            st.session_state.evaluating = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    result = st.session_state.result

    if st.session_state.error:
        st.error(f"Evaluation failed: {st.session_state.error}")
        st.info("Tips: verify your GEMMA_API_KEY in .env, ensure you have internet access, and try a clearer image.")
        if st.button("Grade Another Paper", use_container_width=True):
            reset_state()
            st.rerun()
    else:
        st.markdown('<div class="edu-card">', unsafe_allow_html=True)
        st.markdown('<div class="edu-card-header">Grading Result</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="edu-split-panel">', unsafe_allow_html=True)
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown('<div class="edu-card-header">Source Image</div>', unsafe_allow_html=True)
            st.info("Source image displayed above during capture. Scroll up to review.")

        with right_col:
            st.markdown('<div class="edu-card-header">AI Output</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="edu-feedback-box"><strong>Overall Feedback:</strong><br>{result.get("overall_feedback", "none")}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        tab_extracted, tab_breakdown, tab_feedback = st.tabs(["Extracted Text", "Detailed Breakdown", "Student Feedback"])

        with tab_extracted:
            st.markdown('<div class="edu-card">', unsafe_allow_html=True)
            st.markdown("**Transcribed answer:**")
            st.write(result.get("extracted_text", "none"))
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_breakdown:
            st.markdown('<div class="edu-card">', unsafe_allow_html=True)
            st.markdown(f"**Exam Type:** {result.get('exam_type', 'theory').title()}")
            st.markdown("**Per-Question Breakdown:**")
            breakdown = result.get("question_breakdown", []) or []
            if breakdown:
                for q in breakdown:
                    qn = q.get("question_number", "?")
                    marks_awarded = q.get("marks_awarded", 0)
                    max_marks = q.get("max_marks", 0)
                    if result.get("exam_type") == "objective":
                        is_correct = q.get("is_correct", False)
                        badge = '<span class="edu-badge edu-badge-success">Correct</span>' if is_correct else '<span class="edu-badge edu-badge-danger">Incorrect</span>'
                    else:
                        closeness = q.get("closeness", "")
                        status_map = {"exact": ("edu-badge-success", "Exact"), "close": ("edu-badge-success", "Close"), "partial": ("edu-badge-warning", "Partial"), "incorrect": ("edu-badge-danger", "Incorrect"), "off-topic": ("edu-badge-danger", "Off-topic")}
                        badge_class, badge_text = status_map.get(closeness, ("edu-badge-info", str(closeness)))
                        badge = f'<span class="edu-badge {badge_class}">{badge_text}</span>'
                    st.markdown(f'<div class="edu-question-row"><span class="edu-q-number">Q{qn}</span>{badge}<span class="edu-q-status">{marks_awarded}/{max_marks} marks</span></div>', unsafe_allow_html=True)
                    student_ans = q.get("student_answer", "")
                    if student_ans:
                        st.caption(f"Student: {student_ans}")
                    ref_ans = q.get("correct_answer") or q.get("reference_answer", "")
                    if ref_ans:
                        st.caption(f"Reference: {ref_ans}")
                    q_feedback = q.get("feedback", "")
                    if q_feedback:
                        st.caption(f"Feedback: {q_feedback}")
                    st.divider()
            else:
                st.info("No per-question breakdown returned.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_feedback:
            st.markdown('<div class="edu-card">', unsafe_allow_html=True)
            st.markdown("**Constructive feedback for the student:**")
            st.markdown(f'<div class="edu-feedback-box">{result.get("overall_feedback", "none")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        col_dl_json, col_dl_pdf = st.columns(2)
        result_json = json.dumps(result, indent=2, ensure_ascii=False)
        with col_dl_json:
            st.download_button(label="Download result (JSON)", data=result_json, file_name="edugrade_result.json", mime="application/json", use_container_width=True)
        with col_dl_pdf:
            if FPDF_AVAILABLE:
                try:
                    pdf_bytes = generate_pdf(result, total_marks)
                    st.download_button(label="Download result (PDF)", data=pdf_bytes, file_name="edugrade_result.pdf", mime="application/pdf", use_container_width=True)
                except Exception as exc:
                    st.error(f"PDF generation failed: {exc}")
            else:
                st.button("Download result (PDF)", disabled=True, help="Install fpdf2: pip install fpdf2", use_container_width=True)

        if st.button("Grade Another Paper", use_container_width=True):
            reset_state()
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("EduGrade AI is open source. Built with Streamlit + Google Gemma. Contributions welcome via Hacktoberfest.")
