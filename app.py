import plotly.express as px
import pandas as pd
import streamlit as st
import pdfplumber
from docx import Document
import google.generativeai as genai

# -----------------------------
# PAGE CONFIG (MUST BE FIRST)
# -----------------------------
st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# GEMINI CONFIG
# -----------------------------
try:
    genai.configure(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    # Upgraded to 2.5-flash for perfect compatibility with new auth keys
    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    gemini_enabled = True

except Exception as e:
    gemini_enabled = False
    st.error(
        "Gemini API is not configured correctly."
    )

# -----------------------------
# HEADER
# -----------------------------
st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")
st.info("Upload your resume or paste it below, then paste a job description to get a full AI-powered analysis.")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
resume_text = ""

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
# INPUTS
# -----------------------------
col_res, col_jd = st.columns(2)

with col_res:
    resume = st.text_area("Paste / Verify Your Resume Here", value=resume_text, height=250)

with col_jd:
    job_description = st.text_area("Paste Job Description Here", height=250)

# -----------------------------
# ANALYSIS LOGIC (SESSION STATE)
# -----------------------------
# Initialize session state so reports don't disappear when shifting tabs
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if st.button("Analyze Resume", type="primary"):
    if not resume or not job_description:
        st.warning("Please provide both a resume and a job description.")
    elif not gemini_enabled:
        st.error("Cannot perform analysis. Gemini API is not configured.")
    else:
        with st.spinner("🤖 Remote Pilot AI is scanning your credentials and simulating ATS filtering..."):
            
            # 1. Keyword Math Calculation
            resume_words = set(resume.lower().split())
            job_words = set(job_description.lower().split())
            matched_keywords = resume_words.intersection(job_words)
            missing_keywords = job_words - resume_words

            # 2. Master Prompt to Gemini (Returns everything structured cleanly)
            master_prompt = f"""
            You are an expert corporate Recruiter and an advanced ATS (Applicant Tracking System) parser.
            Analyze the following Resume against the Job Description.

            [RESUME]
            {resume}

            [JOB DESCRIPTION]
            {job_description}

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
            Give 2-3 actionable career recommendations (e.g., certifications to get, project architectures to build) to permanently overcome the skill gaps discovered.

            ### TAILORED COVER LETTER
            Write a professional, compelling, 3-4 paragraph cover letter customized for this applicant applying to this specific role. Include placeholder tags like [Your Name] where appropriate.
            """

            try:
                response = model.generate_content(master_prompt)
                ai_text = response.text

                # Parse sections safely using string partitions
                def extract_section(text, header, next_header=None):
                    try:
                        part = text.split(header)[1]
                        if next_header:
                            part = part.split(next_header)[0]
                        return part.strip()
                    except:
                        return "Section generation misplaced. Please rerun analysis."

                # Save results to session state
                st.session_state.analysis_results = {
                    "score": min(int((len(matched_keywords) / len(job_words)) * 100 + 40), 100) if len(job_words) > 0 else 0, # Balanced score algorithm
                    "matched_count": len(matched_keywords),
                    "missing_skills": sorted(list(missing_keywords)),
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
                st.error(f"An error occurred during AI processing: {str(e)}")

# -----------------------------
# DISPLAY RESULTS TABS
# -----------------------------
if st.session_state.analysis_results:
    res = st.session_state.analysis_results

    # Top KPI Dashboards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall ATS Match Score", f"{res['score']}%")
    with col2:
        st.metric("Matched Keywords Found", res['matched_count'])
    with col3:
        st.metric("Detected Missing Gaps", len(res['missing_skills']))
    
    st.progress(res['score'] / 100)
    st.markdown("---")

    # Render Your 8 Tabs Dynamically
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 ATS Score", "🎯 Skill Gaps", "💡 Interview Tips", 
        "📝 Resume Summary", "🔍 Detailed Analysis", "✍️ Resume Rewrite", 
        "🧠 AI Coach", "✉️ Cover Letter"
    ])

    # 1. ATS SCORE TAB
    with tab1:
        chart_data = pd.DataFrame(
    {
        "Category": [
            "Matched",
            "Missing"
        ],
        "Count": [
            matched,
            len(missing_skills)
        ]
    }
)

fig = px.pie(
    chart_data,
    values="Count",
    names="Category",
    title="Keyword Coverage"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
        st.header("ATS Match Optimization Breakdown")
        st.metric("Calculated Match", f"{res['score']}%")
        if res['score'] >= 80:
            st.success("🏆 **Excellent Alignment:** Your resume shares strong contextual parity with the requirements of this role.")
        elif res['score'] >= 65:
            st.warning("⚡ **Moderate Alignment:** Good base, but adding a few missing target phrases will place you in the top tier.")
        else:
            st.error("❌ **Low Alignment:** Critical keyword gaps found. The automated parsers might filter this out before human eyes see it.")

    # 2. SKILL GAPS TAB
    with tab2:
        st.header("Target Keyword Deficiencies")
        st.write("These specific contextual terms appear in the job description but were missing or phrased differently in your resume:")
        if res['missing_skills']:
            filtered_skills = [s for s in res['missing_skills'] if len(s) > 2 and s.isalpha()]
            st.write(", ".join([f"`{skill}`" for skill in filtered_skills[:20]]))
        else:
            st.success("Phenomenal keyword optimization! No major contextual keyword missing.")

    # 3. INTERVIEW TIPS TAB
    with tab3:
        st.header("Tailored Interview Preparation Simulator")
        st.markdown(res['interview'])

    # 4. RESUME SUMMARY TAB
    with tab4:
        st.header("Objective Profile Summary")
        st.write(res['summary'])
        st.info(f"💡 **Tip:** Use this optimized structural layout in your resume's header segment.")

    # 5. DETAILED ANALYSIS TAB
    with tab5:
        st.header("Comparative Structural Report")
        col_str, col_weak = st.columns(2)
        with col_str:
            st.subheader("✅ Structural Strengths")
            st.markdown(res['strengths'])
        with col_weak:
            st.subheader("⚠️ ATS Bottlenecks & Gaps")
            st.markdown(res['weaknesses'])

    # 6. RESUME REWRITE TAB
    with tab6:
        st.header("ATS-Optimized Phrasing Suggestions")
        st.markdown(res['rewrite'])

    # 7. AI COACH TAB
    with tab7:
        st.header("Strategic Professional Development Plan")
        st.markdown(res['coach'])

    # 8. COVER LETTER TAB
    with tab8:
        st.header("Custom Tailored Cover Letter Generator")
        st.text_area("Generated Output (Editable)", res['cover_letter'], height=450)

if st.button("Test Gemini"):
    try:
        response = model.generate_content(
            "Say hello"
        )
        st.success("Gemini Connected!")
        st.write(response.text)
    except Exception as e:
        st.error(f"Error: {e}")
