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
    model = genai.GenerativeModel(
        "gemini-1.5-flash"
    )
    gemini_enabled = True
except Exception as e:
    gemini_enabled = False
    st.warning("Gemini AI is not configured. Please check your st.secrets file.")

# -----------------------------
# HEADER
# -----------------------------
st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")
st.info("Upload your resume or paste it below, then paste a job description.")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["txt", "pdf", "docx"]
)

resume = ""

if uploaded_file:
    if uploaded_file.name.endswith(".txt"):
        resume = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                resume += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            resume += para.text + "\n"

# -----------------------------
# INPUTS
# -----------------------------
resume = st.text_area(
    "Paste Your Resume Here",
    value=resume,
    height=250
)

job_description = st.text_area(
    "Paste Job Description Here",
    height=250
)

# -----------------------------
# ANALYZE BUTTON
# -----------------------------
if st.button("Analyze Resume"):
    if resume and job_description:
        # Tokenize words for keyword matching calculation
        resume_words = set(resume.lower().split())
        job_words = set(job_description.lower().split())

        matched = len(resume_words.intersection(job_words))
        required = len(job_words)

        score = (
            min(int((matched / required) * 100), 100)
            if required > 0
            else 0
        )

        missing_skills = list(job_words - resume_words)

        # -------------------------
        # TOP METRICS
        # -------------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ATS Score", f"{score}%")
        with col2:
            st.metric("Matched Keywords", matched)
        with col3:
            st.metric("Missing Keywords", len(missing_skills))

        st.progress(score / 100)

        # -------------------------
        # AI ANALYSIS MAIN QUERY
        # -------------------------
        ai_analysis = "AI Analysis is unavailable because Gemini API is not configured."
        
        if gemini_enabled:
            ai_prompt = f"""
            Resume:
            {resume}

            Job Description:
            {job_description}

            Analyze:
            1. ATS Score Improvement
            2. Missing Skills
            3. Resume Strengths
            4. Resume Weaknesses
            5. Career Recommendations
            """
            try:
                ai_response = model.generate_content(ai_prompt)
                ai_analysis = ai_response.text
            except Exception as e:
                ai_analysis = "Failed to generate AI analysis response."

        # -------------------------
        # TABS SETUP
        # -------------------------
        (
            tab1, tab2, tab3, tab4, 
            tab5, tab6, tab7, tab8
        ) = st.tabs([
            "ATS Score", "Skill Gaps", "Interview Tips", 
            "Resume Summary", "Analysis", "Resume Rewrite", 
            "AI Coach", "Cover Letter"
        ])

        # -------------------------
        # TAB 1: ATS Score
        # -------------------------
        with tab1:
            st.metric("ATS Score", f"{score}%")
            if score >= 80:
                st.success("🏆 Excellent Match")
            elif score >= 60:
                st.warning("⚡ Moderate Match")
            else:
                st.error("❌ Low Match")

        # -------------------------
        # TAB 2: Skill Gaps
        # -------------------------
        with tab2:
            st.subheader("Missing Keywords")
            if missing_skills:
                # Display top 15 missing words safely
                st.write(", ".join([f"`{skill}`" for skill in missing_skills[:15]]))
            else:
                st.success("No major skill gaps found.")

        # -------------------------
        # TAB 3: Interview Tips
        # -------------------------
        with tab3:
            st.subheader("Interview Questions & Preparation")
            if gemini_enabled:
                interview_prompt = f"Generate interview questions and sample answers based on this Job Description:\n\n{job_description}"
                try:
                    interview_response = model.generate_content(interview_prompt)
                    st.write(interview_response.text)
                except Exception:
                    st.error("Interview tips generation failed.")
            else:
                st.warning("Gemini AI unavailable.")

        # -------------------------
        # TAB 4: Resume Summary
        # -------------------------
        with tab4:
            word_count = len(resume.split())
            st.write(f"**Resume Length:** {word_count} words")
            st.write(f"**Unique Matching Keywords:** {matched}")

        # -------------------------
        # TAB 5: Analysis
        # -------------------------
        with tab5:
            st.subheader("AI Analysis Breakdown")
            st.write(ai_analysis)

        # -------------------------
        # TAB 6: Resume Rewrite
        # -------------------------
        with tab6:
            st.subheader("Tailored Resume Recommendations")
            if gemini_enabled:
                rewrite_prompt = f"Rewrite this resume professionally to improve ATS compatibility matching this job description.\n\nResume:\n{resume}\n\nJob Description:\n{job_description}"
                try:
                    rewrite_response = model.generate_content(rewrite_prompt)
                    st.text_area("Improved Resume Suggestions", rewrite_response.text, height=400)
                except Exception:
                    st.error("Resume rewrite failed.")
            else:
                st.warning("Gemini AI unavailable.")

        # -------------------------
        # TAB 7: AI Coach
        # -------------------------
        with tab7:
            st.subheader("AI Career Coach Guidance")
            st.write(ai_analysis)

        # -------------------------
        # TAB 8: Cover Letter
        # -------------------------
        with tab8:
            st.subheader("Generated Cover Letter")
            if gemini_enabled:
                cover_prompt = f"Create a professional cover letter using this resume and job description.\n\nResume:\n{resume}\n\nJob Description:\n{job_description}"
                try:
                    cover_response = model.generate_content(cover_prompt)
                    st.text_area("Generated Cover Letter Output", cover_response.text, height=400)
                except Exception:
                    st.error("Cover letter generation failed.")
            else:
                st.warning("Gemini AI unavailable.")
    else:
        st.warning("Please provide both a resume and a job description.")
