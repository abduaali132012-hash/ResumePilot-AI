🚀 ResumePilot AI
Smart Resume Optimization Platform & Career Copilot
ResumePilot AI is an advanced, intelligent career advancement suite engineered to help job seekers bypass rigid corporate automated Applicant Tracking Systems (ATS). Powered by the high-speed Google Gemini API (gemini-2.5-flash), this application performs deep semantic parsing to grade resumes, reveal critical keyword gaps, compare profiles across multiple job roles simultaneously, and generate role-specific career materials.

✨ Core Features
📊 Multi-Format Ingestion: Seamless text extraction from .pdf, .docx, and .txt files using robust programmatic parsers.

🎯 ATS Compatibility Scoring & Analytics: Features a custom mathematical matching engine backed by interactive Plotly Express keyword density charts.

📈 Multi-Job Comparative Benchmarking: Paste up to 3 separate job descriptions simultaneously to see which corporate profile targets your resume fits best.

🔍 Granular Gap Detection: Isolates missing technical skills, critical contextual industry phrases, and structural layout bottlenecks.

✍️ Dynamic Resume Rewriting: Provides targeted summary overhauls and converts weak history text into high-impact, keyword-optimized bullet points.

🧠 Automated AI Career Coaching: Formulates a strategic professional development layout alongside a tailored interview preparation simulator with high-scoring answers.

✉️ Tailored Cover Letter Generator: Automatically compiles a customized, compelling 3-4 paragraph cover letter matched exactly to the core requirements of your primary target role.

📄 Executive Summary Export: Generates on-demand, downloadable PDF summary evaluation forms using ReportLab.

🛠️ Technical Tech Stack
Frontend UI Framework: Streamlit

AI Orchestration Core: Google Generative AI Engine (gemini-2.5-flash)

Data Analytics & Charts: Pandas & Plotly Express

Document Parsers: pdfplumber (PDF) & python-docx (Word)

Document Generation Engine: reportlab (PDF export)

📦 Project Directory Structure
Plaintext
ResumePilot-AI/
├── .streamlit/
│   └── config.toml          # Streamlit custom interface theme options
├── app.py                   # Main Application Entrypoint & Pipeline Core
├── requirements.txt         # Production Dependency Modules
├── LICENSE                  # Proprietary license terms
└── README.md                # Technical documentation handbook
🚀 Getting Started
Clone the repo: git clone [https://github.com/abduaali132012-hash/ResumePilot-AI.git](https://github.com/abduaali132012-hash/ResumePilot-AI.git)

Create a virtual environment and activate it

Install dependencies: pip install -r requirements.txt

Add your Gemini API key to .streamlit/secrets.toml:

Ini, TOML
GEMINI_API_KEY = "your-key-here"
Run locally: streamlit run app.py

🗺️ Roadmap
Done:

✅ Cover letter generator

✅ PDF executive summary export

✅ Open-access feature suite

Planned:

⬜ Resume version history

⬜ Job recommendation engine

⬜ LinkedIn profile analyzer
