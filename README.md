# ResumePilot AI — Hackathon Project Brief

## One-line pitch
ResumePilot AI is a resume-optimization tool that uses Google's Gemini API to score
how well a resume matches a job description, pinpoint missing keywords, and
generate a rewritten resume, interview prep, and a tailored cover letter — all
in one open-access Streamlit web app, no account required.

## The problem
Job seekers rarely know why an application gets rejected before a human ever
reads it — automated Applicant Tracking Systems (ATS) filter resumes on
keyword and structural matching that candidates can't see or test against
themselves.

## The solution
Upload a resume (PDF, DOCX, or TXT) and paste a target job description.
Analysis now runs automatically the moment both fields are filled in — no
button click needed, with quota-safe change detection so it only re-runs
when the content actually changes. ResumePilot AI runs it through Gemini
(`gemini-2.5-flash`) alongside a keyword-overlap scoring engine, then
returns a full breakdown across ten views:

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
10. **Version History** — save each analysis, track your ATS score trend
    across saved versions, reload an older version, and export/import your
    history as JSON

Two more tools work independently of the main analysis, using just the resume:

- **Job Recommendation Engine** — suggests 5 job titles genuinely suited to
  the candidate's background, each with reasoning and job-board search
  keywords
- **LinkedIn Profile Analyzer** — reviews pasted LinkedIn profile text for
  recruiter searchability and checks it for consistency against the resume

A downloadable PDF executive summary is also generated on demand.

## Tech stack
- **Streamlit** — web UI framework
- **Google Gemini API** (`gemini-2.5-flash`), via the `google-genai` SDK — resume/job semantic analysis
  and content generation
- **pdfplumber** / **python-docx** — resume text extraction from PDF/DOCX
- **Pandas** / **Plotly Express** — scoring calculations and charts
- **ReportLab** — PDF report generation

## What I built/fixed during the hackathon window
- Removed a security vulnerability (a hardcoded, unauthenticated server
  endpoint exposed in the public repo)
- Fixed inconsistent ATS scoring logic (two different formulas were
  producing different scores for the same input)
- Added retry handling for transient AI API failures, with logic that
  distinguishes brief transient errors from daily quota exhaustion (retrying
  the latter is pointless and just wastes remaining quota)
- Added an upload size limit to prevent oversized file abuse
- Migrated off the deprecated `google.generativeai` package to `google.genai`
- Built resume version history, a job recommendation engine, and a LinkedIn
  profile analyzer
- Added auto-analyze with change detection, so analysis runs automatically
  without wasting API calls on unrelated interactions
- Prototyped and tested a full subscription/paywall layer (Supabase auth +
  Stripe billing + 7-day free trial) as a monetization path, then
  deliberately descoped it to keep the public submission simple, open-access,
  and dependency-free for judges to run

## Try it live
- **App:** https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app/
- **Repo:** https://github.com/abduaali132012-hash/ResumePilot-AI

## What's next
- Real job-board API integration (currently AI-suggested titles, not live listings)
- Team / recruiter view for agencies managing multiple candidates
- Bulk resume processing
- Arabic-language support
