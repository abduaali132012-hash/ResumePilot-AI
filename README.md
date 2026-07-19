# ResumePilot AI — Hackathon Project Brief

## One-line pitch
ResumePilot AI is a resume-optimization tool that uses Google's Gemini API to score
how well a resume matches a job description, pinpoint missing keywords, and
generate a rewritten resume, interview prep, and a tailored cover letter — all
in one Streamlit web app.

## The problem
Job seekers rarely know why an application gets rejected before a human ever
reads it — automated Applicant Tracking Systems (ATS) filter resumes on
keyword and structural matching that candidates can't see or test against
themselves.

## The solution
Upload a resume (PDF, DOCX, or TXT) and paste a target job description.
ResumePilot AI runs it through Gemini (`gemini-2.5-flash`) alongside a
keyword-overlap scoring engine, then returns a full breakdown across nine
views:

1. **ATS Score** — match percentage with a visual keyword-density chart
2. **Skill Gaps** — the specific keywords missing from the resume
3. **Interview Tips** — role-specific interview questions with sample answers
4. **Resume Summary** — a 3-sentence AI read on the candidate's fit
5. **Detailed Analysis** — strengths, weaknesses, and a 1–10 scoring breakdown
   across Technical Skills, Experience, Leadership, Communication, and ATS
   Compatibility
6. **Resume Rewrite** — an AI-rewritten summary and bullet points optimized
   with the missing keywords
7. **AI Coach** — career development recommendations to close longer-term
   skill gaps
8. **Cover Letter** — a ready-to-edit, tailored 3–4 paragraph cover letter
9. **Job Comparison** — a bar chart comparing fit across up to 3 job postings
   pasted at once

A downloadable PDF executive summary is also generated on demand.

## Tech stack
- **Streamlit** — web UI framework
- **Google Gemini API** (`gemini-2.5-flash`) — resume/job semantic analysis
  and content generation
- **pdfplumber** / **python-docx** — resume text extraction from PDF/DOCX
- **Pandas** / **Plotly Express** — scoring calculations and charts
- **ReportLab** — PDF report generation

## What I built/fixed during the hackathon window
- Removed a security vulnerability (a hardcoded, unauthenticated server
  endpoint exposed in the public repo)
- Fixed inconsistent ATS scoring logic (two different formulas were
  producing different scores for the same input)
- Added retry handling for transient AI API failures
- Added an upload size limit to prevent oversized file abuse
- Prototyped and tested a full subscription/paywall layer (Supabase auth +
  Stripe billing + 7-day free trial) as a monetization path, since ultimately
  descoped back to open access for this submission to keep the demo simple
  and dependency-free for judges

## Try it live
- **App:** https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app/
- **Repo:** https://github.com/abduaali132012-hash/ResumePilot-AI

## What's next
- Resume version history
- Job recommendation engine
- LinkedIn profile analyzer
- Migrating off the deprecated `google.generativeai` package to `google.genai`
