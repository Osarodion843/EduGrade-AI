"""EduGrade AI – Streamlit frontend.

Paper-to-digital grade assistant for overburdened teachers.
Upload a photo of a handwritten answer sheet, provide a marking rubric,
and get an AI-generated grade + constructive feedback powered by Gemma.
"""

from __future__ import annotations

import io
import json
from typing import Optional

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
    max_score = st.number_input(
        "Maximum Score", min_value=0.0, value=10.0, step=0.5
    )

    st.divider()

    rubric = st.text_area(
        "Marking Rubric",
        height=220,
        placeholder=(
            "Paste your marking rubric here. Include expected answers, "
            "criteria, and score allocation.\n\nExample:\n"
            "Q1: Solve 2x + 5 = 15. Expected answer: x = 5. (3 pts)\n"
            "Q2: Define 'photosynthesis'. (2 pts)\n"
            "Total: 10 pts"
        ),
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

col_eval, col_space = st.columns([1, 5])
with col_eval:
    evaluate = st.button(
        "Evaluate Paper",
        type="primary",
        disabled=not (uploaded is not None and rubric.strip() and api_configured()),
        help="Requires an image, a rubric, and a configured API key.",
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
            max_score=max_score,
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
        st.metric("Score", f"{result.get('score', 0)}")
    with m2:
        st.metric("Max Score", f"{result.get('max_score', max_score)}")
    with m3:
        max_s = result.get("max_score", max_score) or 1
        pct = (result.get("score", 0) / max_s) * 100 if max_s else 0
        st.metric("Percentage", f"{pct:.0f}%")

    st.divider()

    tab_extracted, tab_breakdown, tab_feedback = st.tabs(
        ["Extracted Text", "Detailed Breakdown", "Student Feedback"]
    )

    with tab_extracted:
        st.write("**Transcribed answer:**")
        st.write(result.get("extracted_text", "_(none)_"))

    with tab_breakdown:
        st.write("**Points answered correctly:**")
        correct = result.get("points_correct", []) or []
        if correct:
            for pt in correct:
                st.write(f"• {pt}")
        else:
            st.write("_None listed._")

        st.write("**Points missed or incorrect:**")
        missed = result.get("points_missed", []) or []
        if missed:
            for pt in missed:
                st.write(f"• {pt}")
        else:
            st.write("_None listed._")

    with tab_feedback:
        st.write("**Constructive feedback for the student:**")
        st.info(result.get("feedback", "_(none)_"))

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
