import streamlit as st
import pdfplumber
from docx import Document
import pandas as pd
import plotly.express as px
import tempfile
import time
from datetime import datetime, timezone, timedelta
from reportlab.pdfgen import canvas
from supabase import create_client
import stripe
# Updated import for modern Google AI SDK
from google import genai 

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="ResumePilot AI", page_icon="🚀", layout="wide")

st.markdown("# 🚀 ResumePilot AI\n### Smart Resume Optimization Platform\n---")

# -----------------------------
# CLIENT INITIALIZATION
# -----------------------------
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
TRIAL_DAYS = 7

# GOOD: This pulls from the secure dashboard
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# AUTHENTICATION LOGIC
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def do_logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# Apply session tokens if available
if st.session_state.get("access_token"):
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    except:
        do_logout()

if not st.session_state.user:
    st.subheader("Welcome — sign in or create an account")
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                    st.session_state.user = res.user
                    st.session_state.access_token = res.session.access_token
                    st.session_state.refresh_token = res.session.refresh_token
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
    st.stop()

# -----------------------------
# AI GENERATION HELPER
# -----------------------------
def generate_with_retry(prompt, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            # Using updated google.genai syntax
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt == max_attempts - 1: raise e
            time.sleep(2)
    return ""

# ... [KEEP YOUR EXISTING FILE UPLOAD, PROCESSING PIPELINE, AND UI LOGIC HERE] ...
# (Ensure your UI code references `client` instead of `model` if you changed variable names)
