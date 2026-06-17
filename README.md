# 🚀 ResumePilot AI

### *Smart Resume Optimization Platform & Career Copilot*

[![Streamlit App](https://static.streamlit.io/badge_svg.svg)](https://resumepilot-ai.streamlit.app/)
[![GitHub Release](https://img.shields.io/github/v/release/abduaali132012-hash/ResumePilot-AI?color=blue)](https://github.com/abduaali132012-hash/ResumePilot-AI/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ResumePilot AI** is an advanced, intelligent career advancement suite engineered to help job seekers bypass rigid corporate automated Applicant Tracking Systems (ATS). Powered by the high-speed Google Gemini API (`gemini-2.5-flash`), this application performs deep semantic parsing to grade resumes, reveal critical keyword gaps, compare profiles across multiple job roles simultaneously, and generate role-specific career materials.

---

## ✨ Core Features

*   **📊 Multi-Format Ingestion:** Seamless text extraction from `.pdf`, `.docx`, and `.txt` files using robust programmatic parsers.
*   **🎯 ATS Compatibility Scoring & Analytics:** Features a custom mathematical matching engine backed by interactive **Plotly Express** keyword density charts.
*   **📈 Multi-Job Comparative Benchmarking:** Paste up to 3 separate job descriptions simultaneously to see which corporate profile targets your resume fits best.
*   **🔍 Granular Gap Detection:** Isolates missing technical skills, critical contextual industry phrases, and structural layout bottlenecks.
*   **✍️ Dynamic Resume Rewriting:** Provides targeted summary overhauls and converts weak history text into high-impact, keyword-optimized bullet points.
*   **🧠 Automated AI Career Coaching:** Formulates a strategic professional development layout alongside a tailored interview preparation simulator with high-scoring answers.
*   **✉️ Tailored Cover Letter Generator:** Automatically compiles a customized, compelling 3-4 paragraph cover letter matched exactly to the core requirements of your primary target role.
*   **📄 Executive Summary Export:** Generates on-demand, downloadable PDF summary evaluation forms using `ReportLab`.

---

## 🛠️ Technical Tech Stack

*   **Frontend UI Framework:** Streamlit (Dynamic, responsive web runtime configuration)
*   **AI Orchestration Core:** Google Generative AI Engine (`gemini-2.5-flash` model via Google Cloud authorization service layers)
*   **Data Analytics & Charts:** Pandas & Plotly Express 
*   **Document Parsers:** `pdfplumber` (PDF layout text extraction) & `python-docx` (Microsoft Word parsing)
*   **Document Generation Engine:** `reportlab` (Dynamic PDF generator layout compilation)

---

## 📦 Project Directory Structure

```text
ResumePilot-AI/
├── .streamlit/
│   └── config.toml          # Streamlit custom interface theme options
├── app.py                   # Main Application Entrypoint & Pipeline Core
├── requirements.txt         # Production Dependency Modules
├── LICENSE                  # Open-source MIT License terms
└── README.md                # Technical documentation handbook
