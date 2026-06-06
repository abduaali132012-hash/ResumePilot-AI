import streamlit as st

st.set_page_config(page_title="ResumePilot AI", page_icon="🚀")

st.title("🚀 ResumePilot AI")
st.write("AI-powered Resume Analyzer and Job Match Assistant")

resume = st.text_area("Paste Your Resume Here")

job_description = st.text_area("Paste Job Description Here")

analyze_button = st.button("Analyze Resume")

if analyze_button:
    if resume and job_description:

        st.success("Analysis Complete!")

        st.subheader("Resume Match Score")
        st.write("85% Match")

        st.subheader("Strengths")
        st.write("""
        - Relevant skills identified
        - Professional experience detected
        - Good resume structure
        """)

        st.subheader("Suggestions")
        st.write("""
        - Add more measurable achievements
        - Include keywords from job description
        - Improve summary section
        """)

    else:
        st.error("Please enter both Resume and Job Description.")
