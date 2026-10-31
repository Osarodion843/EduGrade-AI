# Implementation Plan: EduGrade AI

This step-by-step roadmap guides the automated build process using **OpenCode** and **Google Gemma via Google GenAI SDK**.

---

## Phase 1: Environment Setup & Project Initialization
- [ ] Initialize local Git repository (`git init`).
- [ ] Create `.gitignore` file excluding `.env`, `__pycache__`, and virtual environments.
- [ ] Create `.env` file with `GEMMA_API_KEY=your_key_here`.
- [ ] Create Python virtual environment and install requirements:
  - `streamlit`
  - `google-genai`
  - `python-dotenv`
  - `pillow` (for image handling)
- [ ] Make initial baseline Git commit: `git commit -m "chore: initial project setup"`.

---

## Phase 2: Core Gemma Multimodal Integration Module
- [ ] Create `gemma_helper.py` to encapsulate API calls.
- [ ] Define the primary prompt template for Gemma:
  - Input: Image object (Pillow), Assignment Topic, Marking Rubric.
  - Instructions: Transcribe text, evaluate according to rubric, return structured JSON response.
- [ ] Test API connectivity with sample handwritten test image.
- [ ] Commit working helper code: `git commit -m "feat: add gemma multimodal evaluation helper"`.

---

## Phase 3: User Interface Development (Streamlit)
- [ ] Create `app.py` with multi-column layout:
  - **Left Sidebar:** API status indicator, Subject/Topic inputs, Marking Rubric text area.
  - **Main Panel:** Image uploader (`st.file_uploader` for JPEG/PNG).
- [ ] Add "Evaluate Paper" trigger button.
- [ ] Add results display view:
  - Metric cards for Score / Max Score.
  - Tabbed sections: "Extracted Text", "Detailed Breakdown", and "Student Feedback".
- [ ] Test end-to-end user flow locally.
- [ ] Commit working UI: `git commit -m "feat: build user interface dashboard"`.

---

## Phase 4: Polish & Open Source Readiness (Hacktoberfest / GitHub)
- [ ] Create `README.md` with:
  - Project Overview & Screenshots.
  - Setup and installation instructions.
  - Hacktoberfest contribution guidelines (`CONTRIBUTING.md`).
- [ ] Verify no secrets or `.env` files are tracked in Git history.
- [ ] Publish repository to GitHub and push `main` branch.