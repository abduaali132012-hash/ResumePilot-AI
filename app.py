import streamlit as st
import time
from google import genai 

# 1. PAGE CONFIG MUST ALWAYS BE FIRST
st.set_page_config(page_title="ResumePilot AI", page_icon="🚀", layout="wide")

# 2. INITIALIZE CLIENT
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. DEFINE FUNCTIONS
def generate_with_retry(prompt, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt == max_attempts - 1: raise e
            time.sleep(2)
    return ""

# 4. UI ELEMENTS
st.markdown("# 🚀 ResumePilot AI\n### Smart Resume Optimization Platform\n---")
st.subheader("Explore ResumePilot Features")

# 5. TABS
tab1, tab2, tab3 = st.tabs(["🎯 ATS Optimizer", "✍️ Cover Letter Generator", "📈 Career Coach"])

with tab1:
    st.markdown("### ATS Compatibility Scoring")
    uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"], key="ats_upload")
    job_desc = st.text_area("Paste the Job Description here")
    
    if st.button("Analyze Resume"):
        st.write("Analysis feature active!")

with tab2:
    st.markdown("### Tailored Cover Letter Generator")
    target_role = st.text_input("Target Job Title")
    if st.button("Generate Cover Letter"):
        st.write("Cover letter generation active!")

with tab3:
    st.markdown("### AI Career Coaching")
    if st.button("Get Coaching Insights"):
        st.write("Coaching insights active!")
