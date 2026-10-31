# Product Requirement Document (PRD)

## Product Name
**EduGrade AI** – Paper-to-Digital Grade Assistant for Overburdened Teachers

---

## 1. Executive Summary
EduGrade AI is an open-source, AI-powered web application created to assist teachers in Africa who manage large, overcrowded classrooms (50–100+ students). The tool enables teachers to upload or capture photos of student handwritten answer sheets, evaluates the responses against a user-provided marking rubric using Google Gemma's multimodal capabilities, and outputs fair grades alongside constructive feedback.

---

## 2. Core Problem & Target Audience
* **Problem:** Teachers spend upwards of 15–20 hours weekly manually grading handwritten tests, leading to burnout, delayed feedback for students, and less time for actual teaching.
* **Target Audience:** Primary and secondary school educators in low-resource and high-density educational environments across Africa.

---

## 3. Key Objectives & Scope
* **Automate Grading:** Reduce grading time per paper from 5 minutes to under 30 seconds.
* **Multimodal Extraction:** Leverage Gemma to transcribe handwritten text from images and compare it to structured scoring rubrics.
* **Constructive Feedback:** Provide personalized, encouraging feedback for each student response.
* **Open Source & Accessible:** Host publicly on GitHub for Hacktoberfest contributions with an intuitive UI.

---

## 4. Key Features & Specifications

### 4.1 Teacher Inputs
1. **Assignment Details:** Subject, Topic, Maximum Score.
2. **Marking Rubric:** Text input specifying expected answers, criteria, and score allocation.
3. **Student Submission:** Image upload (JPEG/PNG) of handwritten paper or direct text input.

### 4.2 AI Processing (Powered by Google Gemma via API)
* Transcribe handwritten text accurately.
* Compare student answer against the provided rubric.
* Assign a numerical score and list key points missed or correctly answered.
* Generate student-facing constructive feedback.

### 4.3 Output Dashboard
* Display original image alongside extracted text for verification.
* Show score breakdown and summary feedback.
* Allow quick copy/download of graded results.

---

## 5. Technical Requirements
* **Frontend/UI:** Streamlit (Python) for rapid prototyping and clean presentation.
* **AI Engine:** Google Gemma (Multimodal via Google GenAI SDK).
* **Version Control:** Git & GitHub (open-source repository with public `.gitignore` protecting API keys).
* **Configuration:** Environment variable management (`.env`).