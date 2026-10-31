"""Gemma multimodal evaluation helper for EduGrade AI.

Encapsulates all calls to Google Gemma (via the Google GenAI SDK) used to:
  1. Transcribe handwritten text from a student answer-sheet image.
  2. Evaluate the transcription against a teacher-provided marking rubric.
  3. Return a structured JSON result (score, breakdown, feedback).

Environment variables:
  GEMMA_API_KEY   - API key for the Google GenAI / Gemma endpoint.
  GEMMA_MODEL     - Model name to use (default: gemma-3).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

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
    # Prompt template
    # ------------------------------------------------------------------

    def _build_prompt(
        self, topic: str, rubric: str, has_teacher_key: bool = False
    ) -> str:
        """Construct the multimodal prompt sent to Gemma.

        The image(s) are appended separately by the caller via the GenAI SDK's
        multi-part content support. This returns the text portion that
        instructs the model on what to do with the images.
        """
        teacher_key_section = ""
        if has_teacher_key:
            teacher_key_section = (
                "\nTEACHER'S ANSWER KEY (REFERENCE):\n"
                "One or more images of the teacher's own completed answer sheet "
                "are provided alongside the student's sheet. Use the teacher's "
                "key as the authoritative reference for what constitutes a correct "
                "answer. Cross-check the student's transcription against the "
                "teacher's key before scoring.\n"
            )

        return (
            "You are an experienced teacher grading a handwritten answer sheet. "
            "Follow these steps exactly and return ONLY a valid JSON object "
            "(no markdown fences, no extra text).\n\n"
            f"ASSIGNMENT TOPIC: {topic}\n\n"
            f"MARKING RUBRIC:\n{rubric}\n\n"
            f"{teacher_key_section}"
            "TASK:\n"
            "1. Transcribe the student's handwritten answer from the image as "
            "accurately as possible (preserve the original wording where legible).\n"
            "2. Compare the transcribed answer against the marking rubric above, "
            "and against the teacher's answer key if one is provided.\n"
            "3. Assign a numerical score (0 to the rubric's maximum).\n"
            "4. List key points the student answered correctly.\n"
            "5. List key points missed or answered incorrectly.\n"
            "6. Write concise, encouraging, student-facing constructive feedback.\n\n"
            "OUTPUT SCHEMA (JSON):\n"
            "{\n"
            '  "extracted_text": "<verbatim transcription>",\n'
            '  "score": <number>,\n'
            '  "max_score": <number from rubric>,\n'
            '  "points_correct": ["<point>", ...],\n'
            '  "points_missed": ["<point>", ...],\n'
            '  "feedback": "<student-facing constructive feedback>"\n'
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
        teacher_images: Optional[list[Image.Image]] = None,
        max_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluate a handwritten answer-sheet image against a rubric.

        Args:
            image: PIL Image of the student's handwritten paper.
            topic: Assignment topic / subject.
            rubric: Teacher-provided marking rubric text.
            teacher_images: Optional list of PIL Images of the teacher's own
                completed answer sheet(s), used as the authoritative answer key.
            max_score: Optional override for the maximum possible score.

        Returns:
            Parsed JSON dict with keys: extracted_text, score, max_score,
            points_correct, points_missed, feedback.
        """
        prompt = self._build_prompt(
            topic, rubric, has_teacher_key=bool(teacher_images)
        )

        contents: list[Any] = [prompt]
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
                "extracted_text": "",
                "score": 0,
                "max_score": max_score or 0,
                "points_correct": [],
                "points_missed": [],
                "feedback": "Could not parse the model's JSON response.",
                "_raw_response": raw_text,
            }

        # Normalise expected fields with sensible defaults.
        data.setdefault("extracted_text", "")
        data.setdefault("points_correct", [])
        data.setdefault("points_missed", [])
        data.setdefault("feedback", "")
        if max_score is not None:
            data["max_score"] = max_score
        data.setdefault("max_score", 0)
        data.setdefault("score", 0)

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
