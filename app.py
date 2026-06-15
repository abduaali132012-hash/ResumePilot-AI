import google.generativeai as genai
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)
import streamlit as st
import pdfplumber
from docx import Document
from reportlab.pdfgen import canvas
import tempfile
import pandas as pd
import plotly.express as px

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# HEADER
# ----------------------------------

st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")

st.info(
    "Upload your resume or paste it below, then paste a job description."
)

# ----------------------------------
# FILE UPLOAD
# ----------------------------------

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

# ----------------------------------
# INPUTS
# ----------------------------------

resume = st.text_area(
    "Paste Your Resume Here",
    value=resume,
    height=250
)

job_description = st.text_area(
    "Paste Job Description Here",
    height=250
)

# ----------------------------------
# ANALYZE BUTTON
# ----------------------------------

if st.button("Analyze Resume"):

    if resume and job_description:

       prompt = f"""
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

response = model.generate_content(prompt)

ai_analysis = response.text 

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

        # --------------------------
        # TOP METRICS
        # --------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("ATS Score", f"{score}%")

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

        # --------------------------
        # PDF REPORT
        # --------------------------

        pdf_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        c = canvas.Canvas(pdf_file.name)

        c.drawString(
            100,
            800,
            "ResumePilot AI Report"
        )

        c.drawString(
            100,
            770,
            f"ATS Score: {score}%"
        )

        c.save()

        with open(pdf_file.name, "rb") as f:

            st.download_button(
                "📄 Download PDF Report",
                f,
                file_name="ResumePilot_Report.pdf"
            )

        # --------------------------
        # TABS
        # --------------------------

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            [
                "ATS Score",
                "Skill Gaps",
                "Interview Tips",
                "Resume Summary",
                "Analysis",
                "Resume Rewrite"
            ]
        )

        # --------------------------
        # TAB 1
        # --------------------------

        with tab1:

            st.metric(
                "ATS Score",
                f"{score}%"
            )

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

        # --------------------------
        # TAB 2
        # --------------------------

        with tab2:

            st.subheader("Missing Keywords")

            if missing_skills:

                for skill in missing_skills[:10]:
                    st.error(skill)

            else:

                st.success(
                    "No major skill gaps found."
                )

        # --------------------------
        # TAB 3
        # --------------------------

        with tab3:

            st.subheader(
                "Suggested Interview Questions"
            )

           interview_prompt = f"""
Generate interview questions
and strong sample answers
for this job.

Job Description:

{job_description}
"""

interview_response = model.generate_content(
    interview_prompt
)

st.write(
    interview_response.text
)

        # --------------------------
        # TAB 4
        # --------------------------

        with tab4:

            st.subheader("Resume Summary")

            word_count = len(
                resume.split()
            )

            st.write(
                f"📄 Resume Length: {word_count} words"
            )

            st.write(
                f"✅ Matching Keywords: {matched}"
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

        # --------------------------
        # TAB 5
        # --------------------------

        with tab5:

            skills_data = pd.DataFrame(
{
"Category":[
"Matched",
"Missing"
],
"Count":[
matched,
len(missing_skills)
]
}
)

fig = px.bar(
skills_data,
x="Category",
y="Count",
title="Keyword Analysis"
)

st.plotly_chart(
fig,
use_container_width=True
)

            st.subheader("Strength Analysis")

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

            st.subheader("AI Suggestions")

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

        # --------------------------
        # TAB 6
        # --------------------------

        with tab6:

        rewrite_prompt = f"""
Rewrite this resume professionally.

Resume:

{resume}

Job Description:

{job_description}

Improve ATS compatibility.
"""

rewrite_response = model.generate_content(
    rewrite_prompt
)

rewritten_resume = rewrite_response.text

st.text_area(
    "Improved Resume",
    rewritten_resume,
    height=400
)
    else:

        st.warning(
            "Please provide both a resume and a job description."
        )

tab7

with tab7:

    st.subheader(
        "🤖 Gemini Career Coach"
    )

    st.write(ai_analysis)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
[
"ATS Score",
"Skill Gaps",
"Interview Tips",
"Resume Summary",
"Analysis",
"Resume Rewrite",
"AI Coach"
]
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(

    with tab8:

    cover_prompt = f"""
Create a professional cover letter.

Resume:

{resume}

Job Description:

{job_description}
"""

    cover_letter = model.generate_content(
        cover_prompt
    )

    st.text_area(
        "Generated Cover Letter",
        cover_letter.text,
        height=400
    )
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
