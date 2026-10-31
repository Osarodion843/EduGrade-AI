"""Gemma multimodal evaluation helper for EduGrade AI.

Encapsulates all calls to Google Gemma (via the Google GenAI SDK) used to:
  1. Transcribe handwritten text from a student answer-sheet image.
  2. Evaluate the transcription against a teacher-provided marking rubric.
  3. Support Objective (binary: full marks or zero) and Theory (partial credit)
     exam types with per-question marks and teacher answer-key reference.
  4. Return a structured JSON result with per-question breakdown.

Environment variables:
  GEMMA_API_KEY   - API key for the Google GenAI / Gemma endpoint.
  GEMMA_MODEL     - Model name to use (default: gemma-4-26b-a4b-it).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from PIL import Image

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

GEMMA_API_KEY: Optional[str] = os.getenv("GEMMA_API_KEY")
GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")


class GemmaHelper:
    """Thin wrapper around the Google GenAI client for Gemma."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMMA_API_KEY
        self.model = model or GEMMA_MODEL

        if not self.api_key or self.api_key == "your_key_here":
            raise ValueError(
                "GEMMA_API_KEY is not configured. Set it in your .env file "
                "(see .env for the placeholder)."
            )

        self.client = genai.Client(api_key=self.api_key)

    # ------------------------------------------------------------------
    # Prompt templates
    # ------------------------------------------------------------------

    def _format_question_marks(self, question_marks: List[Dict[str, Any]]) -> str:
        """Format the per-question marks specification for the prompt."""
        lines = []
        for qm in question_marks:
            qn = qm.get("question_number")
            marks = qm.get("marks")
            lines.append(f"  Question {qn}: {marks} mark(s)")
        return "\n".join(lines)

    def _build_objective_prompt(
        self,
        topic: str,
        rubric: str,
        question_marks: List[Dict[str, Any]],
        has_teacher_key: bool,
    ) -> str:
        """Build the prompt for Objective exams (binary: full marks or zero)."""
        teacher_key_section = ""
        if has_teacher_key:
            teacher_key_section = (
                "\nTEACHER'S ANSWER KEY (REFERENCE - AUTHORITATIVE):\n"
                "One or more images of the teacher's own completed objective "
                "answer sheet are provided (showing handwritten answers such as "
                "A, B, C, D for each question number). Use these as the "
                "definitive source for the correct answer to each objective "
                "question.\n"
            )

        qm_section = self._format_question_marks(question_marks)
        total_marks = sum(qm.get("marks", 0) for qm in question_marks)

        return (
            "You are an experienced teacher grading OBJECTIVE (multiple-choice / "
            "short-answer) exam papers. Follow these steps exactly and return "
            "ONLY a valid JSON object (no markdown fences, no extra text).\n\n"
            f"ASSIGNMENT TOPIC: {topic}\n\n"
            f"MARKING RUBRIC / INSTRUCTIONS:\n{rubric}\n\n"
            f"{teacher_key_section}"
            "PER-QUESTION MARKS SCHEME (each question is independent):\n"
            f"{qm_section}\n"
            f"TOTAL MAXIMUM SCORE: {total_marks}\n\n"
            "TASK:\n"
            "1. Transcribe the student's handwritten answer for EACH question from "
            "the image as accurately as possible (e.g., Q1: C, Q2: A).\n"
            "2. For each objective question, compare the student's handwritten "
            "letter answer (A/B/C/D or similar) against the teacher's answer key "
            "and the marking rubric.\n"
            "3. OBJECTIVE GRADING RULE (strict binary):\n"
            "   - If the student's answer matches the correct answer -> award the "
            "FULL marks for that question.\n"
            "   - If the student's answer is INCORRECT, blank, or unreadable -> "
            "award ZERO marks for that question.\n"
            "   - There is NO partial credit for objective questions.\n"
            "4. Compute the total score as the sum of marks awarded across all "
            "questions.\n"
            "5. Write concise, encouraging, student-facing constructive feedback.\n\n"
            "OUTPUT SCHEMA (JSON):\n"
            "{\n"
            '  "exam_type": "objective",\n'
            '  "topic": "<topic>",\n'
            '  "total_score": <number>,\n'
            '  "max_score": <number>,\n'
            '  "question_breakdown": [\n'
            "    {\n"
            '      "question_number": <integer>,\n'
            '      "student_answer": "<transcribed answer letter>",\n'
            '      "correct_answer": "<correct answer letter from teacher key>",\n'
            '      "is_correct": <true/false>,\n'
            '      "marks_awarded": <number>,\n'
            '      "max_marks": <number>,\n'
            '      "feedback": "<brief per-question feedback>"\n'
            "    }\n"
            "  ],\n"
            '  "overall_feedback": "<student-facing constructive feedback>"\n'
            "}\n"
        )

    def _build_theory_prompt(
        self,
        topic: str,
        rubric: str,
        question_marks: List[Dict[str, Any]],
        has_teacher_key: bool,
    ) -> str:
        """Build the prompt for Theory exams (partial credit allowed)."""
        teacher_key_section = ""
        if has_teacher_key:
            teacher_key_section = (
                "\nTEACHER'S MARKING GUIDE (REFERENCE - AUTHORITATIVE):\n"
                "One or more images of the teacher's own completed theory answer "
                "sheet / marking guide are provided. Use these as the reference "
                "standard for what constitutes a complete, correct answer to each "
                "theory question.\n"
            )

        qm_section = self._format_question_marks(question_marks)
        total_marks = sum(qm.get("marks", 0) for qm in question_marks)

        return (
            "You are an experienced teacher grading THEORY (essay / structured) "
            "exam papers. Follow these steps exactly and return ONLY a valid JSON "
            "object (no markdown fences, no extra text).\n\n"
            f"ASSIGNMENT TOPIC: {topic}\n\n"
            f"MARKING RUBRIC / INSTRUCTIONS:\n{rubric}\n\n"
            f"{teacher_key_section}"
            "PER-QUESTION MARKS SCHEME:\n"
            f"{qm_section}\n"
            f"TOTAL MAXIMUM SCORE: {total_marks}\n\n"
            "TASK:\n"
            "1. Transcribe the student's handwritten answer for EACH question from "
            "the image as accurately as possible (preserve original wording where "
            "legible).\n"
            "2. For each theory question, compare the student's answer against "
            "the teacher's marking guide and the marking rubric.\n"
            "3. THEORY GRADING RULE (partial credit allowed):\n"
            "   - Assess how CLOSE the student's answer is to the teacher's "
            "marking guide answer.\n"
            "   - Do NOT require word-for-word matching.\n"
            "   - Award marks proportionally based on closeness and correctness:\n"
            "     * Exact / fully correct -> FULL marks\n"
            "     * Very close, minor omission -> NEAR-FULL marks (e.g. 80-90%)\n"
            "     * Half correct / some relevant points -> PARTIAL marks "
            "(e.g. 40-60%)\n"
            "     * Totally wrong / irrelevant / off-topic -> ZERO marks\n"
            "   - Use your professional judgement; be fair and encouraging.\n"
            "4. Compute the total score as the sum of marks awarded across all "
            "questions.\n"
            "5. Write concise, encouraging, student-facing constructive feedback.\n\n"
            "OUTPUT SCHEMA (JSON):\n"
            "{\n"
            '  "exam_type": "theory",\n'
            '  "topic": "<topic>",\n'
            '  "total_score": <number>,\n'
            '  "max_score": <number>,\n'
            '  "question_breakdown": [\n'
            "    {\n"
            '      "question_number": <integer>,\n'
            '      "student_answer": "<transcribed answer>",\n'
            '      "reference_answer": "<reference from teacher marking guide>",\n'
            '      "closeness": "<exact|close|partial|incorrect|off-topic>",\n'
            '      "marks_awarded": <number>,\n'
            '      "max_marks": <number>,\n'
            '      "feedback": "<brief per-question feedback>"\n'
            "    }\n"
            "  ],\n"
            '  "overall_feedback": "<student-facing constructive feedback>"\n'
            "}\n"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_paper(
        self,
        image: Image.Image,
        topic: str,
        rubric: str,
        exam_type: str = "theory",
        question_marks: Optional[List[Dict[str, Any]]] = None,
        teacher_images: Optional[List[Image.Image]] = None,
        max_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluate a handwritten answer-sheet image against a marking guide.

        Args:
            image: PIL Image of the student's handwritten paper.
            topic: Assignment topic / subject.
            rubric: Teacher-provided marking rubric / instructions text.
            exam_type: "objective" (binary full/zero) or "theory"
                (partial credit allowed).
            question_marks: List of dicts like
                [{"question_number": 1, "marks": 2}, ...].
            teacher_images: Optional list of PIL Images of the teacher's own
                completed answer sheet(s) / marking guide, used as the
                authoritative reference.
            max_score: Optional override for the maximum possible score.

        Returns:
            Parsed JSON dict with exam_type, total_score, max_score,
            question_breakdown, overall_feedback, extracted_text.
        """
        if question_marks is None:
            question_marks = [{"question_number": 1, "marks": max_score or 10}]

        if exam_type == "objective":
            prompt = self._build_objective_prompt(
                topic, rubric, question_marks, has_teacher_key=bool(teacher_images)
            )
        else:
            prompt = self._build_theory_prompt(
                topic, rubric, question_marks, has_teacher_key=bool(teacher_images)
            )

        contents: List[Any] = [prompt]
        if teacher_images:
            contents.extend(teacher_images)
        contents.append(image)

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )

        raw_text = getattr(response, "text", "") or ""
        return self._parse_response(raw_text, max_score)

    def test_connection(self) -> bool:
        """Lightweight connectivity check against the Gemma endpoint."""
        try:
            test_image = Image.new("RGB", (10, 10), color="white")
            self.evaluate_paper(
                image=test_image,
                topic="connection test",
                rubric="Maximum score: 1. Award 1 if the image is blank white.",
                exam_type="objective",
                question_marks=[{"question_number": 1, "marks": 1}],
                max_score=1,
            )
            return True
        except Exception:  # noqa: BLE001 - connectivity check should never crash
            return False

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(raw_text: str, max_score: Optional[float]) -> Dict[str, Any]:
        """Parse Gemma's response into a dict, tolerating minor formatting noise."""
        cleaned = raw_text.strip()

        # Strip accidental markdown fences if the model added them.
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            # Remove an optional language tag on the first line.
            cleaned = "\n".join(cleaned.split("\n")[1:]) if "\n" in cleaned else cleaned
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: return the raw text so the UI can surface it for debugging.
            return {
                "exam_type": "theory",
                "extracted_text": "",
                "total_score": 0,
                "max_score": max_score or 0,
                "question_breakdown": [],
                "overall_feedback": "Could not parse the model's JSON response.",
                "_raw_response": raw_text,
            }

        # Normalise expected fields with sensible defaults.
        data.setdefault("exam_type", "theory")
        data.setdefault("topic", "")
        data.setdefault("extracted_text", "")
        data.setdefault("question_breakdown", [])
        data.setdefault("overall_feedback", "")
        if max_score is not None:
            data["max_score"] = max_score
        data.setdefault("max_score", 0)
        data.setdefault("total_score", 0)

        # Ensure each breakdown entry has required fields.
        normalised_breakdown = []
        for entry in data.get("question_breakdown", []):
            normalised_breakdown.append(
                {
                    "question_number": entry.get("question_number", 0),
                    "student_answer": entry.get("student_answer", ""),
                    "correct_answer": entry.get("correct_answer", ""),
                    "reference_answer": entry.get("reference_answer", ""),
                    "is_correct": entry.get("is_correct", False),
                    "closeness": entry.get("closeness", ""),
                    "marks_awarded": entry.get("marks_awarded", 0),
                    "max_marks": entry.get("max_marks", 0),
                    "feedback": entry.get("feedback", ""),
                }
            )
        data["question_breakdown"] = normalised_breakdown

        return data


# ---------------------------------------------------------------------------
# Convenience module-level helper (optional, for quick scripts)
# ---------------------------------------------------------------------------

_helper: Optional[GemmaHelper] = None


def get_helper() -> GemmaHelper:
    """Return a singleton GemmaHelper instance."""
    global _helper
    if _helper is None:
        _helper = GemmaHelper()
    return _helper
