import pandas as pd
import streamlit as st
import pdfplumber
from docx import Document

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# -------------------------------
# Header
# -------------------------------

st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")

st.sidebar.title("🚀 ResumePilot AI")

st.sidebar.markdown("---")

st.sidebar.info(
    "Analyze resumes, identify skill gaps, and improve ATS compatibility."
)

st.sidebar.markdown("### Features")

st.sidebar.success("ATS Score")
st.sidebar.success("Skill Gap Analysis")
st.sidebar.success("Resume Summary")
st.sidebar.success("Interview Preparation")
st.sidebar.success("AI Suggestions")

st.info(
    "Upload your resume or paste it below, then paste a job description."
)

# -------------------------------
# Resume Upload
# -------------------------------

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

# -------------------------------
# Resume Text Area
# -------------------------------

resume = st.text_area(
    "Paste Your Resume Here",
    value=resume,
    height=200
)

# -------------------------------
# Job Description
# -------------------------------

job_description = st.text_area(
    "Paste Job Description Here",
    height=200
)

# -------------------------------
# Analyze Button
# -------------------------------

if st.button("Analyze Resume"):

    if resume and job_description:

        resume_words = set(resume.lower().split())
        job_words = set(job_description.lower().split())

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

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "ATS Score",
                "Skill Gaps",
                "Interview Tips",
                "Resume Summary",
                "Analysis"
            ]
        )

        # --------------------------------
        # ATS Score
        # --------------------------------

        with tab1:

            st.metric(
                "ATS Score",
                f"{score}%"
            )

            st.progress(score / 100)

            if score >= 80:
                st.balloons()

            st.progress(score / 100)

            if score >= 80:
                st.success(
                    "🏆 Excellent ATS Match"
                )

            elif score >= 60:
                st.warning(
                    "⚡ Moderate ATS Match"
                )

            else:
                st.error(
                    "❌ Low ATS Match"
                )

        # --------------------------------
        # Skill Gaps
        # --------------------------------

        with tab2:

            st.subheader("Missing Keywords")

            if missing_skills:

                for skill in missing_skills[:10]:
                    st.error(skill)

            else:
                st.success(
                    "No major skill gaps found."
                )

        # --------------------------------
        # Interview Tips
        # --------------------------------

        with tab3:

            st.subheader(
                "Suggested Interview Questions"
            )

            questions = [
                "Tell me about yourself.",
                "What projects have you worked on?",
                "Why are you interested in this role?",
                "What are your strengths and weaknesses?",
                "How do you solve technical problems?"
            ]

            for q in questions:
                st.write(f"• {q}")

        # --------------------------------
        # Resume Summary
        # --------------------------------

        with tab4:

            st.subheader("Resume Summary")

            st.subheader("Keyword Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Matched Keywords",
                    matched
                )

            with col2:
                st.metric(
                    "Missing Keywords",
                    len(missing_skills)
                 )

            word_count = len(
                resume.split()
            )

            skills_found = len(
                resume_words.intersection(
                    job_words
                )
            )

            st.write(
                f"📄 Resume Length: {word_count} words"
            )

            st.write(
                f"✅ Matching Keywords: {skills_found}"
            )

            if word_count < 150:

                st.warning(
                    "Resume appears too short."
                )

            elif word_count > 800:

                st.warning(
                    "Resume may be too long."
                )

            else:

                st.success(
                    "Resume length looks good."
                )

        # --------------------------------
        # Analysis
        # --------------------------------

        with tab5:

            st.subheader("Strength Analysis")

            st.subheader("Keyword Analysis")

            data = pd.DataFrame({
                "Category": [
                    "Matched",
                    "Missing"
                 ],
                 "Count": [
                     matched,
                     len(missing_skills)
                 ]
               })

               st.bar_chart(
                   data.set_index("Category")
               )

            strengths = []

            if score >= 70:
                strengths.append(
                    "Strong keyword alignment"
                )

            if len(resume.split()) > 150:
                strengths.append(
                    "Detailed resume content"
                )

            if strengths:

                for item in strengths:
                    st.success(item)

            else:

                st.warning(
                    "No major strengths detected."
                )

            st.subheader(
                "Weakness Analysis"
            )

            if missing_skills:

                for skill in missing_skills[:5]:

                    st.error(
                        f"Missing keyword: {skill}"
                    )

            else:

                st.success(
                    "No major weaknesses detected."
                )

            st.subheader(
                "AI Suggestions"
            )

            st.info(
                "Add missing keywords from the job description."
            )

            st.info(
                "Quantify achievements with numbers."
            )

            st.info(
                "Customize your resume for each application."
            )

            st.info(
                "Highlight relevant projects and certifications."
            )

            st.markdown("---")

            st.subheader(
                "Overall Match Rating"
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

    else:

        st.warning(
            "Please provide both a resume and a job description."
        )

report = f"""
ResumePilot AI Report

ATS Score: {score}%

Matched Keywords: {matched}

Missing Keywords:
{', '.join(missing_skills[:20])}
"""

st.download_button(
    "📥 Download Report",
    report,
    file_name="ResumePilot_Report.txt"
)
