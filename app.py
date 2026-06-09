st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 ResumePilot AI")
st.subheader("AI-Powered Resume Analyzer & Career Assistant")
st.info(
    "Paste your resume and target job description below. ResumePilot AI will compare them and provide recommendations."
)
Upload Resume
OR
Paste Resume
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["txt"]
)
if uploaded_file:
    resume = uploaded_file.read().decode("utf-8")
