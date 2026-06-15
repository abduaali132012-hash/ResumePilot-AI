import streamlit as st
import pdfplumber
from docx import Document
import google.generativeai as genai

# -----------------------------
# GEMINI CONFIG
# -----------------------------

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# HEADER
# -----------------------------

st.title("🚀 ResumePilot AI")
st.subheader(
    "AI-Powered Resume Analyzer & Career Assistant"
)

st.info(
    "Upload your resume or paste it below, then paste a job description."
)

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

        resume_words = set(
            resume.lower().split()
        )

        job_words = set(
            job_description.lower().split()
        )

        matched = len(
            resume_words.intersection(job_words)
        )

        required = len(job_words)

        score = (
            min(
                int((matched / required) * 100),
                100
            )
            if required > 0
            else 0
        )

        missing_skills = list(
            job_words - resume_words
        )

        # -------------------------
        # TOP METRICS
        # -------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "ATS Score",
                f"{score}%"
            )

        with col2:
            st.metric(
                "Matched Keywords",
                matched
            )

        with col3:
            st.metric(
                "Missing Keywords",
                len(missing_skills)
            )

        st.progress(score / 100)

        # -------------------------
        # AI ANALYSIS
        # -------------------------

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

        ai_response = model.generate_content(
            ai_prompt
        )

        ai_analysis = ai_response.text

        # -------------------------
        # TABS
        # -------------------------

        (
            tab1,
            tab2,
            tab3,
            tab4,
            tab5,
            tab6,
            tab7,
            tab8
        ) = st.tabs(
            [
                "ATS Score",
                "Skill Gaps",
                "Interview Tips",
                "Resume Summary",
                "Analysis",
                "Resume Rewrite",
                "AI Coach",
                "Cover Letter"
            ]
        )

        # -------------------------
        # TAB 1
        # -------------------------

        with tab1:

            st.metric(
                "ATS Score",
                f"{score}%"
            )

            if score >= 80:
                st.success(
                    "🏆 Excellent Match"
                )

            elif score >= 60:
                st.warning(
                    "⚡ Moderate Match"
                )

            else:
                st.error(
                    "❌ Low Match"
                )

        # -------------------------
        # TAB 2
        # -------------------------

        with tab2:

            st.subheader(
                "Missing Keywords"
            )

            if missing_skills:

                for skill in missing_skills[:10]:
                    st.error(skill)

            else:

                st.success(
                    "No major skill gaps found."
                )

        # -------------------------
        # TAB 3
        # -------------------------

        with tab3:

            interview_prompt = f"""
Generate interview questions and answers.

Job Description:

{job_description}
"""

            interview_response = (
                model.generate_content(
                    interview_prompt
                )
            )

            st.write(
                interview_response.text
            )

        # -------------------------
        # TAB 4
        # -------------------------

        with tab4:

            word_count = len(
                resume.split()
            )

            st.write(
                f"Resume Length: {word_count} words"
            )

            st.write(
                f"Matching Keywords: {matched}"
            )

        # -------------------------
        # TAB 5
        # -------------------------

        with tab5:

            st.subheader(
                "AI Analysis"
            )

            st.write(
                ai_analysis
            )

        # -------------------------
        # TAB 6
        # -------------------------

        with tab6:

            rewrite_prompt = f"""
Rewrite this resume professionally.

Resume:

{resume}

Job Description:

{job_description}

Improve ATS compatibility.
"""

            rewrite_response = (
                model.generate_content(
                    rewrite_prompt
                )
            )

            st.text_area(
                "Improved Resume",
                rewrite_response.text,
                height=400
            )

        # -------------------------
        # TAB 7
        # -------------------------

        with tab7:

            st.subheader(
                "AI Career Coach"
            )

            st.write(
                ai_analysis
            )

        # -------------------------
        # TAB 8
        # -------------------------

        with tab8:

            cover_prompt = f"""
Create a professional cover letter.

Resume:

{resume}

Job Description:

{job_description}
"""

            cover_response = (
                model.generate_content(
                    cover_prompt
                )
            )

            st.text_area(
                "Generated Cover Letter",
                cover_response.text,
                height=400
            )

    else:

        st.warning(
            "Please provide both a resume and a job description."
        )
