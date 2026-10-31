# EduGrade AI

**Paper-to-Digital Grade Assistant for Overburdened Teachers**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.66-red.svg)](https://streamlit.io)
[![Google Gemma](https://img.shields.io/badge/AI-Google%20Gemma-green.svg)](https://ai.google.dev/gemma)
[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-friendly-orange.svg)](https://hacktoberfest.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

EduGrade AI is an open-source, AI-powered web application that helps teachers in Africa manage large, overcrowded classrooms (50–100+ students) by automating the grading of handwritten answer sheets.

Teachers upload a photo of a student's handwritten paper, provide a marking rubric, and EduGrade AI uses **Google Gemma** (multimodal) to transcribe the handwriting, evaluate it against the rubric, assign a fair grade, and generate constructive student feedback — cutting grading time from ~5 minutes to under 30 seconds per paper.

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Demo

Run locally:

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/edugrade-ai.git
cd edugrade-ai

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your Gemma API key
# Copy .env.example to .env and add your key:
#   GEMMA_API_KEY=your_actual_key_here
#   GEMMA_MODEL=gemma-4-26b-a4b-it

# 5. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Features

- **Handwritten transcription** — Gemma multimodal model transcribes student answers from uploaded JPEG/PNG images.
- **Two exam types:**
  - **Objective** — Binary grading: correct answer = full marks, incorrect/blank = zero marks. No partial credit.
  - **Theory** — Partial credit allowed: AI assesses how close the student's answer is to the teacher's marking guide (exact, close, partial, incorrect, off-topic) and awards marks proportionally — never requiring word-for-word matching.
- **Per-question marks** — Teacher specifies how many marks each question carries (single value or comma-separated list per question).
- **Teacher answer key / marking guide** — Upload your own completed answer sheet image(s); the AI uses them as the authoritative reference for grading.
- **Rubric-based grading** — Compares the transcribed answer against a teacher-provided marking rubric and assigns a numerical score.
- **Constructive feedback** — Generates encouraging, student-facing feedback plus per-question breakdown.
- **Results dashboard** — View the original image alongside extracted text, score breakdown, and detailed feedback.
- **Export results** — Download graded results as JSON for record-keeping.
- **Open source** — Public GitHub repository welcoming Hacktoberfest contributions.

---

## Exam Types

### Objective Exams

Best for multiple-choice, fill-in-the-blank, or short-answer questions.

- The teacher specifies how many marks each question carries.
- A correct answer earns the **full marks** for that question.
- An incorrect, blank, or unreadable answer earns **zero marks**.
- No partial credit is awarded.

### Theory Exams

Best for essay, structured, or descriptive questions.

- The teacher specifies how many marks each question carries.
- The AI assesses how **close** the student's answer is to the teacher's marking guide:
  - **Exact / fully correct** → full marks
  - **Close** (minor omission) → near-full marks (e.g., 80–90%)
  - **Partial** (some relevant points) → partial marks (e.g., 40–60%)
  - **Incorrect / off-topic** → zero marks
- Answers are **not** required to match word-for-word; partial credit is awarded fairly.

### Setting Marks per Question

In the sidebar, under "Question Configuration":

- Enter the **Number of Questions**.
- Enter **Marks per Question** as either:
  - A single number (e.g. `2`) applied to all questions, or
  - A comma-separated list (e.g. `2,3,2,5,3`) with one value per question in order.

The total maximum score is calculated automatically.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend/UI | [Streamlit](https://streamlit.io) (Python) |
| AI Engine | [Google Gemma](https://ai.google.dev/gemma) via [Google GenAI SDK](https://github.com/googleapis/python-genai) |
| Image handling | [Pillow](https://python-pillow.org) |
| Config | `python-dotenv` (environment variables via `.env`) |
| Version control | Git & GitHub (public, Hacktoberfest-friendly) |

---

## Project Structure

```
edugrade-ai/
├── app.py                 # Streamlit frontend
├── gemma_helper.py        # Gemma multimodal evaluation helper
├── requirements.txt       # Python dependencies
├── .env                   # API keys (gitignored — never commit)
├── .env.example           # Example environment file (commit this)
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT license
├── README.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
└── implementation_plan.md # Original implementation roadmap
├── product_requirement_document_prd.md # Product requirements
```

> ⚠️ **Security:** Never commit your `.env` file. It contains your `GEMMA_API_KEY`. The repo's `.gitignore` already excludes it. Use `.env.example` to document required variables without exposing secrets.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- A Google GenAI / Gemma API key ([Get one here](https://aistudio.google.com/app/apikey))

### Steps

```bash
# Clone
git clone https://github.com/<your-username>/edugrade-ai.git
cd edugrade-ai

# Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env and paste your GEMMA_API_KEY

# Run
streamlit run app.py
```

### Environment variables (`.env`)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GEMMA_API_KEY` | Yes | Your Google GenAI API key | `AQ.Ab8RN...` |
| `GEMMA_MODEL` | No | Gemma model to use | `gemma-4-26b-a4b-it` |

---

## Usage

1. **Sidebar:** Enter Subject, Topic, Maximum Score, and paste your Marking Rubric.
2. **Main panel:** Upload a photo (JPEG/PNG) of the student's handwritten answer sheet.
3. Click **Evaluate Paper**.
4. View results across three tabs:
   - **Extracted Text** — the model's transcription of the handwriting.
   - **Detailed Breakdown** — points correct and points missed.
   - **Student Feedback** — encouraging, constructive feedback.
5. Click **Download result (JSON)** to save the graded output.

---

## Screenshots

> _Screenshots coming soon — contributions welcome!_

| Sidebar (inputs) | Results dashboard |
|------------------|-------------------|
| ![](docs/screenshots/sidebar.png) | ![](docs/screenshots/results.png) |

Add your own screenshots under `docs/screenshots/` and reference them here — a great first Hacktoberfest issue!

---

## Contributing

EduGrade AI is open source and **Hacktoberfest-friendly**. We welcome contributions from developers, designers, educators, and testers.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to set up the dev environment
- How to submit a pull request
- Code style and commit conventions
- Issue labels good for first-time contributors

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built for teachers in low-resource, high-density classrooms across Africa.
- Powered by [Google Gemma](https://ai.google.dev/gemma) and [Streamlit](https://streamlit.io).
- Created as part of an AWS hackathon.

---

_Made with ❤️ for overburdened teachers._
