<p align="center">
  <img src="assets/hero-image.png" alt="ResumePilot AI Hero Image" width="100%">
</p>

# ResumePilot AI 🚀

> **An all-in-one, AI-powered career platform and resume-optimisation suite built with Google Gemini API and Streamlit.**

[![Live Demo](https://img.shields.io/badge/Streamlit-Live%20App-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/abduaali132012-hash/ResumePilot-AI)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

## 🌟 Overview
ResumePilot AI is a comprehensive career acceleration platform. Job seekers rarely know why an application gets rejected before a human reads it because automated Applicant Tracking Systems (ATS) filter resumes on invisible keyword and structural matches. 

ResumePilot AI instantly analyzes resumes against target job descriptions, pinpoints missing keywords, generates professional rewrites, and scales into a full suite of career growth tools—all in one open-access web app, with zero account required.

---

## 🛠️ Complete Feature Suite

### Core ATS Optimization & Analysis
1. **ATS Score & Keyword Density** — Match percentage with visual keyword charts and overlap scoring.
2. **Skill Gaps** — Specific keywords missing from your resume relative to the job description.
3. **Interview Tips** — Role-specific interview questions with tailored sample answers.
4. **Resume Summary** — A 3-sentence AI evaluation of candidate fit.
5. **Detailed Scoring Breakdown** — Granular 1–10 scoring across Technical Skills, Experience, Leadership, Communication, and ATS Compatibility.
6. **AI Resume Rewrite** — Instantly generates an optimized professional summary and bullet points injected with missing keywords.
7. **AI Career Coach** — Personalized career development recommendations to close longer-term skill gaps.
8. **Tailored Cover Letter** — Ready-to-edit, custom 3–4 paragraph professional cover letter.
9. **Job Comparison** — Bar chart comparing fit across up to 3 job postings pasted simultaneously.
10. **Version History** — Save analyses, track ATS score trends across saved versions, reload past versions, and export/import history as JSON.

### Advanced Career Growth Tools (Beyond ATS)
* **Job Recommendation Engine** — Suggests 5 job titles suited to the candidate's background with reasoning and search keywords.
* **LinkedIn Profile Analyzer** — Reviews pasted LinkedIn profile text for recruiter searchability and verifies consistency against the resume.
* **Application Tracker & Salary Insights** — Manage your active pipeline and benchmark role compensations.
* **Downloadable Executive Summary** — Generate a professional PDF report on demand.

---

## 📸 Screenshots

| Dashboard & Overview | ATS & Keyword Analysis |
| :---: | :---: |
| ![Dashboard](assets/dashboard.png) | ![ATS Analysis](assets/ats-analysis.png) |

| AI Resume Rewrite | LinkedIn Profile Analyzer |
| :---: | :---: |
| ![Resume Rewrite](assets/resume-rewrite.png) | ![LinkedIn Analyzer](assets/linkedin-analyzer.png) |

| Job Matching & Comparison | Application Tracker |
| :---: | :---: |
| ![Job Matching](assets/job-matching.png) | ![Application Tracker](assets/application-tracker.png) |

---

## 💻 Tech Stack & Architecture
* **Frontend / UI:** [Streamlit](https://streamlit.io/) (Interactive web framework)
* **AI Engine:** Google Gemini API (`gemini-2.5-flash`) via the official `google-genai` SDK for semantic analysis and content generation.
* **Document Processing:** `pdfplumber` / `python-docx` for reliable text extraction from PDF, DOCX, and TXT files.
* **Data & Visualization:** Pandas & Plotly Express for metrics, scoring calculations, and dynamic charts.
* **Report Generation:** ReportLab for on-demand PDF executive summaries.

---

## ⚙️ Key Engineering Highlights
* **Auto-Analysis with Change Detection:** Automatically runs analysis the moment both resume and job description fields are populated without requiring extra button clicks, saving API overhead.
* **Quota-Safe Error Handling:** Built robust retry logic distinguishing transient API errors from daily quota exhaustion to preserve resources.
* **Security & Cleanup:** Removed hardcoded server endpoint exposures and added file size limits to prevent oversized uploads.
* **Streamlined Architecture:** Prototyped a complete Supabase/Stripe paywall layer before intentionally descoping it to keep the submission open-access and dependency-free for judges.

---

## 🚀 Try It Live & Resources
* **Live Web App:** [Access ResumePilot AI](https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app/)[cite: 1]
* **Pitch Deck (PDF):** [View Investor Pitch Deck (PDF)](assets/resumepilot-pitch-deck.pdf)
* **Demo Video:** [Watch Video Walkthrough](https://example.com/demo-video) *(Link your recorded .mp4 demo here)*

---

## 🗺️ Product Roadmap

### Completed (v1.0)
- [x] Resume Upload & PDF/DOCX Parsing
- [x] ATS Match Score & Keyword Gap Analysis
- [x] AI Resume Rewrite & Cover Letter Generation
- [x] LinkedIn Profile Analyzer
- [x] Job Recommendation Engine & Comparison Tool
- [x] Version History & JSON Export/Import
- [x] PDF Executive Summary Export

### Coming Soon (v2.0)
- [ ] Real-time Job Board API Integrations
- [ ] AI Interview Coach Simulator (Interactive Voice/Text Q&A)
- [ ] Recruiter Portal & Team Analytics Dashboard
- [ ] Multilingual Support (Arabic & Regional Languages)

---

## 👨‍💻 Author
**Abdu Ali Adem**
* GitHub: [@abduaali132012-hash](https://github.com/abduaali132012-hash)
* Portfolio / Project Repository: [ResumePilot-AI](https://github.com/abduaali132012-hash/ResumePilot-AI)[cite: 1]
