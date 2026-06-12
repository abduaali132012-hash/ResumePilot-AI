import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# Header
st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")

st.info(
    "Upload your resume or paste it below, then paste a job description."
)

# Resume Upload
uploaded_file = st.file_uploader(
    "Upload Resume (.txt)",
    type=["txt"]
)

resume = ""

if uploaded_file:
    resume = uploaded_file.read().decode("utf-8")

# Resume Text Area
resume = st.text_area(
    "Paste Your Resume Here",
    value=resume,
    height=200
)

# Job Description
job_description = st.text_area(
    "Paste Job Description Here",
    height=200
)

# Analyze Button
if st.button("Analyze Resume"):

    if resume and job_description:

        resume_words = set(resume.lower().split())
        job_words = set(job_description.lower().split())

        matched = len(resume_words.intersection(job_words))
        required = len(job_words)

        score = min(
            int((matched / required) * 100),
            100
        ) if required > 0 else 0

        missing_skills = list(job_words - resume_words)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "ATS Score",
                "Skill Gaps",
                "Interview Tips",
                "Resume Summary",
                "Analysis"
            ]
        )

        with tab1:
            st.metric("ATS Score", f"{score}%")

        with tab2:
            st.subheader("Missing Keywords")

            if missing_skills:
                for skill in missing_skills[:10]:
                    st.error(skill)
            else:
                st.success("No major skill gaps found.")

        with tab3:
            st.subheader("Interview Questions")

            questions = [
                "Tell me about yourself.",
                "What projects have you worked on?",
                "Why are you interested in this role?",
                "What are your strengths and weaknesses?"
            ]

            for q in questions:
                st.write(f"• {q}")

        with tab4:
            word_count = len(resume.split())

            st.subheader("Resume Summary")
            st.write(f"Resume Length: {word_count} words")

        with tab5:
            st.subheader("Analysis")

            if score >= 80:
                st.success("🏆 Excellent Match")
            elif score >= 60:
                st.warning("⚡ Moderate Match")
            else:
                st.error("❌ Low Match")

    else:
        st.warning(
            "Please provide both a resume and a job description."
        )
