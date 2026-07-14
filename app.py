import streamlit as st
import pdfplumber
from docx import Document
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import tempfile
import time
from reportlab.pdfgen import canvas

# -----------------------------
# PAGE CONFIG (MUST BE THE FIRST STREAMLIT COMMAND)
# -----------------------------
st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# Banner rendered immediately AFTER page config
st.markdown("""
# 🚀 ResumePilot AI
### Smart Resume Optimization Platform
---
""")

# -----------------------------
# GEMINI CONFIG
# -----------------------------
try:
    genai.configure(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
    model = genai.GenerativeModel("gemini-2.5-flash")
    gemini_enabled = True
except Exception as e:
    gemini_enabled = False
    st.error("Gemini API is not configured correctly.")

# -----------------------------
# HELPER CORE FUNCTIONS
# -----------------------------
def calculate_score(resume_text, jd, boost=0):
    """
    Returns an ATS match score from 0-100.
    `boost` is an optional flat bonus (used for the primary/displayed score,
    since raw keyword overlap tends to look harsher than a recruiter's
    real impression). Keeping this in ONE function means every score
    shown in the app is calculated the same way.
    """
    if not resume_text or not jd:
        return 0
    resume_words = set(resume_text.lower().split())
    job_words = set(jd.lower().split())
    matched = len(resume_words.intersection(job_words))
    required = len(job_words)
    if required == 0:
        return 0
    return min(int((matched / required) * 100) + boost, 100)

def generate_with_retry(prompt, max_attempts=3, delay_seconds=2):
    """
    Calls Gemini and retries a couple of times on transient failures
    (rate limits, brief network hiccups) instead of giving up on the
    first blip. Raises the last error if every attempt fails, so the
    caller's try/except can still show a message to the user.
    """
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(delay_seconds)
    raise last_error

# -----------------------------
# FILE UPLOAD SYSTEM
# -----------------------------
MAX_UPLOAD_MB = 5

uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
resume_text = ""

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_UPLOAD_MB:
        st.error(f"File is {file_size_mb:.1f}MB. Please upload a resume under {MAX_UPLOAD_MB}MB.")
        uploaded_file = None

if uploaded_file:
    if uploaded_file.name.endswith(".txt"):
        resume_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + "\n"

# -----------------------------
# TWO-COLUMN DATA INPUTS
# -----------------------------
col_res, col_jd = st.columns(2)

with col_res:
    resume = st.text_area("Paste / Verify Your Resume Here", value=resume_text, height=400)

with col_jd:
    st.markdown("### Target Job Descriptions")
    job1 = st.text_area("Primary Job Description (Used for Main Analysis)", height=150)
    job2 = st.text_area("Comparison Job Description 2 (Optional)", height=120)
    job3 = st.text_area("Comparison Job Description 3 (Optional)", height=120)

# -----------------------------
# PROCESSING PIPELINE
# -----------------------------
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if st.button("Analyze Resume", type="primary"):
    if not resume or not job1:
        st.warning("Please provide at least a resume and the Primary Job Description.")
    elif not gemini_enabled:
        st.error("Cannot perform analysis. Gemini API is not configured.")
    else:
        with st.spinner("🤖 Remote Pilot AI is scanning your credentials and simulating ATS filtering..."):
            
            # Primary Keyword Calculations
            resume_words = set(resume.lower().split())
            job_words = set(job1.lower().split())
            matched_keywords = resume_words.intersection(job_words)
            missing_keywords = job_words - resume_words

            # Multi-Job Comparative Logic Calculations
            score1 = calculate_score(resume, job1)
            score2 = calculate_score(resume, job2) if job2 else 0
            score3 = calculate_score(resume, job3) if job3 else 0

            # Combined prompts for optimal single-token parsing
            master_prompt = f"""
            You are an expert corporate Recruiter and an advanced ATS parser.
            Analyze the following Resume against the Primary Job Description.

            [RESUME]
            {resume}

            [JOB DESCRIPTION]
            {job1}

            Provide a comprehensive evaluation divided explicitly into these sections using these exact headers:
            
            ### RESUME SUMMARY
            Provide a short, 3-sentence professional summary of the candidate's background relative to this job.

            ### CORE STRENGTHS
            List 3 major strengths or matching qualifications found in the resume.

            ### CRITICAL WEAKNESSES
            List 2-3 main gaps or formatting blocks keeping this resume from passing recruiters.

            ### INTERVIEW PREPARATION
            Provide 3 realistic interview questions tailored to this job role, along with high-scoring sample answers or talking points for this candidate.

            ### RESUME REWRITE SUGGESTIONS
            Provide a restructured, high-impact rewrite of the candidate's professional summary and their top experience bullet points, optimized with keywords to rank highly.

            ### CAREER COACH GUIDANCE
            Give 2-3 actionable career recommendations to permanently overcome the skill gaps discovered.

            ### TAILORED COVER LETTER
            Write a professional, compelling, 3-4 paragraph cover letter customized for this applicant applying to this specific role. Include placeholder tags like [Your Name] where appropriate.
            """

            scoring_prompt = f"""
            Score this resume from 1-10 on these parameters. Return your complete answer strictly formatted as markdown bullet points:
            - **Technical Skills**: [Score]/10
            - **Experience**: [Score]/10
            - **Leadership**: [Score]/10
            - **Communication**: [Score]/10
            - **ATS Compatibility**: [Score]/10

            Resume: {resume}
            Job Description: {job1}
            """

            try:
                # Each call retries automatically a couple of times on
                # transient failures before giving up.
                ai_text = generate_with_retry(master_prompt)
                score_text = generate_with_retry(scoring_prompt)

                def extract_section(text, header, next_header=None):
                    try:
                        part = text.split(header)[1]
                        if next_header:
                            part = part.split(next_header)[0]
                        return part.strip()
                    except IndexError:
                        # This means `header` literally wasn't found in the
                        # AI's response text. Printing to the terminal/logs
                        # lets YOU see it (users won't), so you can tell
                        # whether Gemini is drifting from the expected format.
                        print(f"[extract_section] Header not found: {header!r}")
                        return "Section layout mismatched. Please try analyzing again."

                # Commit metrics data mapping objects directly to permanent memory
                st.session_state.analysis_results = {
                    "score": calculate_score(resume, job1, boost=40),
                    "matched_count": len(matched_keywords),
                    "missing_skills": sorted(list(missing_keywords)),
                    "score1": score1,
                    "score2": score2,
                    "score3": score3,
                    "ai_score_breakdown": score_text,
                    "summary": extract_section(ai_text, "### RESUME SUMMARY", "### CORE STRENGTHS"),
                    "strengths": extract_section(ai_text, "### CORE STRENGTHS", "### CRITICAL WEAKNESSES"),
                    "weaknesses": extract_section(ai_text, "### CRITICAL WEAKNESSES", "### INTERVIEW PREPARATION"),
                    "interview": extract_section(ai_text, "### INTERVIEW PREPARATION", "### RESUME REWRITE SUGGESTIONS"),
                    "rewrite": extract_section(ai_text, "### RESUME REWRITE SUGGESTIONS", "### CAREER COACH GUIDANCE"),
                    "coach": extract_section(ai_text, "### CAREER COACH GUIDANCE", "### TAILORED COVER LETTER"),
                    "cover_letter": ai_text.split("### TAILORED COVER LETTER")[-1].strip()
                }
                st.success("Analysis Complete!")
            except Exception as e:
                error_text = str(e).lower()
                if "429" in error_text or "quota" in error_text or "rate" in error_text:
                    st.error("Gemini is rate-limiting requests right now. Please wait a minute and try again.")
                else:
                    st.error(f"An error occurred during AI processing: {str(e)}")

# -----------------------------
# RUNTIME UI DRAW RE-RENDER INTERFACE
# -----------------------------
if st.session_state.analysis_results:
    res = st.session_state.analysis_results

    # Top Metric Dashboard Cards Array
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("ATS Match Score", f"{res['score']}%")
    with m_col2:
        st.metric("Matched Keywords", res['matched_count'])
    with m_col3:
        st.metric("Missing Gaps", len(res['missing_skills']))
    with m_col4:
        word_count = len(resume.split()) if resume else 0
        st.metric("Resume Word Count", word_count if word_count > 0 else "—")
    
    st.progress(res['score'] / 100)
    
    # -----------------------------
    # ON-DEMAND GENERATE PDF ENGINE
    # -----------------------------
    try:
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(pdf_file.name)
        c.drawString(100, 800, "ResumePilot AI Assessment Report")
        c.drawString(100, 770, f"Primary ATS Score: {res['score']}%")
        c.drawString(100, 740, f"Matched Keywords Found: {res['matched_count']}")
        c.drawString(100, 710, f"Missing Keywords Logged: {len(res['missing_skills'])}")
        c.save()
        
        with open(pdf_file.name, "rb") as f:
            st.download_button(
                label="📄 Download Executive Summary PDF Report",
                data=f,
                file_name="ResumePilot_Report.pdf",
                mime="application/pdf"
            )
    except Exception as pdf_err:
        st.info("PDF Summary compilation engine currently idling.")

    st.markdown("---")

    # Render Your Updated 9 Tabs System
    tabs = st.tabs([
        "📊 ATS Score", "🎯 Skill Gaps", "💡 Interview Tips", 
        "📝 Resume Summary", "🔍 Detailed Analysis", "✍️ Resume Rewrite", 
        "🧠 AI Coach", "✉️ Cover Letter", "📈 Job Comparison"
    ])

    # Tab 1: ATS SCORE LAYOUT WITH PLOTLY PIE CHART
    with tabs[0]:
        st.header("ATS Match Optimization Breakdown")
        
        # Build Dataframe safely using dynamic variables mapped from session memory
        chart_data = pd.DataFrame({
            "Category": ["Matched Keywords", "Missing Deficiencies"],
            "Count": [res['matched_count'], max(len(res['missing_skills']), 1)]
        })
        fig = px.pie(chart_data, values="Count", names="Category", title="Core Keyword Metric Density Coverage")
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("Calculated Primary Matching Factor", f"{res['score']}%")
        if res['score'] >= 80:
            st.success("🏆 **Excellent Alignment:** Your profile shares close parity with the requirements of this role.")
        elif res['score'] >= 65:
            st.warning("⚡ **Moderate Alignment:** Good base, but missing target terms should be blended in.")
        else:
            st.error("❌ **Low Alignment:** Significant keyword gaps found. Automated parsers could reject this early.")

    # Tab 2: SKILL GAPS
    with tabs[1]:
        st.header("Target Keyword Deficiencies")
        st.write("These terms appear in your target specifications but were absent or phrased differently in your resume layout:")
        if res['missing_skills']:
            filtered_skills = [s for s in res['missing_skills'] if len(s) > 2 and s.isalpha()]
            st.write(", ".join([f"`{skill}`" for skill in filtered_skills[:30]]))
        else:
            st.success("Phenomenal keyword optimization! No major contextual metrics missing.")

    # Tab 3: INTERVIEW PREPARATION
    with tabs[2]:
        st.header("Tailored Interview Preparation Simulator")
        st.markdown(res['interview'])

    # Tab 4: RESUME SUMMARY
    with tabs[3]:
        st.header("Objective Profile Summary")
        st.write(res['summary'])

    # Tab 5: DETAILED ANALYSIS & RAW SCORES
    with tabs[4]:
        st.header("Comparative Structural Report")
        col_str, col_weak = st.columns(2)
        with col_str:
            st.subheader("✅ Structural Strengths")
            st.markdown(res['strengths'])
        with col_weak:
            st.subheader("⚠️ ATS Bottlenecks & Gaps")
            st.markdown(res['weaknesses'])
        
        st.markdown("---")
        st.subheader("AI Scoring Breakdown Matrix")
        st.markdown(res['ai_score_breakdown'])

    # Tab 6: REWRITE SUGGESTIONS
    with tabs[5]:
        st.header("ATS-Optimized Phrasing Suggestions")
        st.markdown(res['rewrite'])

    # Tab 7: CAREER COACHING
    with tabs[6]:
        st.header("Strategic Professional Development Plan")
        st.markdown(res['coach'])

    # Tab 8: TARGET COVER LETTER
    with tabs[7]:
        st.header("Custom Tailored Cover Letter Generator")
        st.text_area("Generated Output (Editable)", res['cover_letter'], height=450)

    # Tab 9: MULTI-JOB SCORING COMPARISON GRAPH
    with tabs[8]:
        st.header("Multi-Job Intent Target Comparison Chart")
        comparison_dict = {
            "Primary Job (Job 1)": res['score1'],
            "Comparison Job 2": res['score2'],
            "Comparison Job 3": res['score3']
        }
        st.bar_chart(comparison_dict)
        st.info("Use this visual data array to see which job profile variant matches best with your current resume version.")

# -----------------------------
# SIDEBAR BACKEND TEST BUTTONS
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Infrastructure Connectivity Diagnostics")

if st.sidebar.button("Test Gemini Connection"):
    try:
        response = model.generate_content("Say hello")
        st.sidebar.success(f"Gemini Active: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# NOTE: The old "Test AMD Llama Node" button hardcoded a raw server IP
# address directly in source code that was pushed to a PUBLIC GitHub repo.
# That let anyone reading your code hit your server directly, with no
# authentication. It has been removed entirely.
#
# If you need to test a second/local LLM endpoint later, put the URL in
# .streamlit/secrets.toml (which is .gitignored, so it never reaches GitHub)
# and read it with st.secrets["LLAMA_NODE_URL"] instead of typing it here.
