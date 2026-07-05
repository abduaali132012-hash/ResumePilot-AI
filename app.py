import streamlit as st
import pdfplumber
from docx import Document
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import tempfile
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
def generate_with_retry(prompt, retries=1):
    """Call Gemini, retrying once on transient failures before giving up."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            last_error = e
            print(f"[generate_with_retry] attempt {attempt + 1} failed: {e}")
    raise last_error

def calculate_score(resume_text, jd):
    if not resume_text or not jd:
        return 0
    resume_words = set(resume_text.lower().split())
    job_words = set(jd.lower().split())
    matched = len(resume_words.intersection(job_words))
    required = len(job_words)
    return int((matched / required) * 100) if required > 0 else 0

# -----------------------------
# FILE UPLOAD SYSTEM
# -----------------------------
MAX_UPLOAD_MB = 5

uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
resume_text = ""

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_UPLOAD_MB:
        st.error(f"File is {file_size_mb:.1f}MB. Please upload a file under {MAX_UPLOAD_MB}MB.")
        st.stop()

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
                response = generate_with_retry(master_prompt)
                ai_text = response.text

                score_response = generate_with_retry(scoring_prompt)
                score_text = score_response.text

                def extract_section(text, header, next_header=None):
                    try:
                        part = text.split(header)[1]
                        if next_header:
                            part = part.split(next_header)[0]
                        return part.strip()
                    except Exception as extract_err:
                        # Print to the terminal/logs running the app so you can see
                        # exactly what went wrong instead of guessing.
                        print(f"[extract_section error] header={header!r} -> {extract_err}")
                        return "Section layout mismatched. Please try analyzing again."

                st.session_state.analysis_results = {
                    "score": score1,
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
                print(f"[AI processing error] {e}")
                st.error(
                    "Something went wrong while analyzing your resume. "
                    "This is usually temporary — please try clicking Analyze again in a moment."
                )

if st.session_state.analysis_results:
    res = st.session_state.analysis_results

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("ATS Match Score", f"{res['score']}%")
    with m_col2:
        st.metric("Matched Keywords", res['matched_count'])
    with m_col3:
        st.metric("Missing Gaps", len(res['missing_skills']))
    with m_col4:
        st.metric("Resume Word Count", len(resume.split()))
    
    st.progress(res['score'] / 100)
    
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

    tabs = st.tabs([
        "📊 ATS Score", "🎯 Skill Gaps", "💡 Interview Tips", 
        "📝 Resume Summary", "🔍 Detailed Analysis", "✍️ Resume Rewrite", 
        "🧠 AI Coach", "✉️ Cover Letter", "📈 Job Comparison"
    ])

    with tabs[0]:
        st.header("ATS Match Optimization Breakdown")
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

    with tabs[1]:
        st.header("Target Keyword Deficiencies")
        st.write("These terms appear in your target specifications but were absent or phrased differently in your resume layout:")
        if res['missing_skills']:
            filtered_skills = [s for s in res['missing_skills'] if len(s) > 2 and s.isalpha()]
            st.write(", ".join([f"`{skill}`" for skill in filtered_skills[:30]]))
        else:
            st.success("Phenomenal keyword optimization! No major contextual metrics missing.")

    with tabs[2]:
        st.header("Tailored Interview Preparation Simulator")
        st.markdown(res['interview'])

    with tabs[3]:
        st.header("Objective Profile Summary")
        st.write(res['summary'])

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

    with tabs[5]:
        st.header("ATS-Optimized Phrasing Suggestions")
        st.markdown(res['rewrite'])

    with tabs[6]:
        st.header("Strategic Professional Development Plan")
        st.markdown(res['coach'])

    with tabs[7]:
        st.header("Custom Tailored Cover Letter Generator")
        st.text_area("Generated Output (Editable)", res['cover_letter'], height=450)

    with tabs[8]:
        st.header("Multi-Job Intent Target Comparison Chart")
        comparison_dict = {
            "Primary Job (Job 1)": res['score1'],
            "Comparison Job 2": res['score2'],
            "Comparison Job 3": res['score3']
        }
        st.bar_chart(comparison_dict)
        st.info("Use this visual data array to see which job profile variant matches best with your current resume version.")

st.sidebar.markdown("---")
st.sidebar.subheader("Infrastructure Connectivity Diagnostics")

if st.sidebar.button("Test Gemini Connection"):
    try:
        response = model.generate_content("Say hello")
        st.sidebar.success(f"Gemini Active: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# NOTE: The old "Test AMD Llama Node" button called a hardcoded, unauthenticated
# IP address. That's a security risk in a public repo (anyone can see and hit it),
# so it has been removed. If you need a second model provider later, load its
# address from st.secrets instead of typing it directly into the code.
