import streamlit as st

st.set_page_config(page_title="ResumePilot AI")

st.title("ResumePilot AI")
st.subheader("AI-Powered Resume Analysis Assistant")

resume = st.text_area("Paste your Resume")

job_description = st.text_area("Paste Job Description")

if st.button("Analyze"):
if resume and job_description:
st.success("Analysis Complete!")

```
    st.write("### Suggested Improvements")
    st.write("- Add more job-specific keywords")
    st.write("- Highlight measurable achievements")
    st.write("- Include relevant technical skills")

    st.write("### ATS Score")
    st.write("75/100")

    st.write("### Interview Preparation")
    st.write("Prepare examples demonstrating your experience and accomplishments.")
else:
    st.warning("Please enter both Resume and Job Description.")
```
