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
"Upload your resume or paste it below, then paste a job description. ResumePilot AI will compare them and provide recommendations."
)

# Resume Upload

uploaded_file = st.file_uploader(
"Upload Resume (.txt)",
type=["txt"]
)

resume = ""

if uploaded_file:
resume = uploaded_file.read().decode("utf-8")

# Manual Resume Input

resume = st.text_area(
"Paste Your Resume Here",
value=resume,
height=200
)

# Job Description Input

job_description = st.text_area(
"Paste Job Description Here",
height=200
)

# Analyze Button

if st.button("Analyze Resume"):

```
if resume and job_description:

    resume_words = set(resume.lower().split())
    job_words = set(job_description.lower().split())

    matched = len(resume_words.intersection(job_words))
    required = len(job_words)

    score = min(
        int((matched / required) * 100),
        100
    ) if required > 0 else 0

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        ["ATS Score", "Skill Gaps", "Interview Tips"]
    )

    with tab1:
        st.metric("ATS Score", f"{score}%")

    with tab2:
        missing_skills = list(job_words - resume_words)

        st.write("### Missing Keywords")

        if missing_skills:
            for skill in missing_skills[:10]:
                st.write(f"❌ {skill}")
        else:
            st.success("No major skill gaps found!")

    with tab3:
        st.subheader("Suggested Interview Questions")

        questions = [
            "Tell me about yourself.",
            "What projects have you worked on?",
            "How do you solve technical problems?",
            "What are your strengths and weaknesses?",
            "Why are you interested in this role?"
        ]

        for q in questions:
            st.write(f"• {q}")

else:
    st.warning(
        "Please provide both a resume and a job description."
    )
```
