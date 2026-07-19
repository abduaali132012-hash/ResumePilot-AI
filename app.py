import streamlit as st
import pdfplumber
from docx import Document
from google import genai
import pandas as pd
import plotly.express as px
import tempfile
import time
import json
import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas

# -----------------------------
# PAGE CONFIG (MUST BE THE FIRST STREAMLIT COMMAND)
# -----------------------------
st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="🚀",
    layout="wide"
)

# Banner rendered immediately AFTER page config
st.markdown("""
# 🚀 ResumePilot AI
### Smart Resume Optimization Platform
---
""")

# -----------------------------
# GEMINI CONFIG
# -----------------------------
try:
    gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_MODEL = "gemini-2.5-flash"
    gemini_enabled = True
except Exception as e:
    gemini_enabled = False
    st.error("Gemini API is not configured correctly.")

# -----------------------------
# HELPER CORE FUNCTIONS
# -----------------------------
def calculate_score(resume_text, jd, boost=0):
    """
    Returns an ATS match score from 0-100.
    `boost` is an optional flat bonus (used for the primary/displayed score,
    since raw keyword overlap tends to look harsher than a recruiter's
    real impression). Keeping this in ONE function means every score
    shown in the app is calculated the same way.
    """
    if not resume_text or not jd:
        return 0
    resume_words = set(resume_text.lower().split())
    job_words = set(jd.lower().split())
    matched = len(resume_words.intersection(job_words))
    required = len(job_words)
    if required == 0:
        return 0
    return min(int((matched / required) * 100) + boost, 100)

def generate_with_retry(prompt, max_attempts=3, delay_seconds=2):
    """
    Calls Gemini and retries a couple of times on transient failures
    (brief network hiccups, momentary rate limits) instead of giving up on
    the first blip. Does NOT retry on daily quota exhaustion (HTTP 429 with
    a per-day quota message) — a short delay can't fix a limit that only
    resets once a day, so retrying there would just burn through whatever
    quota is left even faster.
    """
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL, contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            error_text = str(e).lower()
            is_daily_quota_exhausted = "429" in error_text and (
                "perday" in error_text.replace(" ", "").lower() or "quota exceeded" in error_text
            )
            if is_daily_quota_exhausted:
                break  # no point retrying — won't recover until tomorrow
            if attempt < max_attempts:
                time.sleep(delay_seconds)
    raise last_error

# -----------------------------
# FILE UPLOAD SYSTEM
# -----------------------------
MAX_UPLOAD_MB = 5

uploaded_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
resume_text = ""

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_UPLOAD_MB:
        st.error(f"File is {file_size_mb:.1f}MB. Please upload a resume under {MAX_UPLOAD_MB}MB.")
        uploaded_file = None

if uploaded_file:
    if uploaded_file.name.endswith(".txt"):
        resume_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + "\n"

# -----------------------------
# TWO-COLUMN DATA INPUTS
# -----------------------------
# If a version was just loaded from the History tab, it overrides whatever
# was uploaded/typed, so the person sees their older draft restored.
resume_default = st.session_state.pop("_reload_resume", None) or resume_text
job1_default = st.session_state.pop("_reload_job1", "")

col_res, col_jd = st.columns(2)

with col_res:
    resume = st.text_area("Paste / Verify Your Resume Here", value=resume_default, height=400)

with col_jd:
    st.markdown("### Target Job Descriptions")
    job1 = st.text_area("Primary Job Description (Used for Main Analysis)", value=job1_default, height=150)
    job2 = st.text_area("Comparison Job Description 2 (Optional)", height=120)
    job3 = st.text_area("Comparison Job Description 3 (Optional)", height=120)

# -----------------------------
# LINKEDIN PROFILE INPUT (manual paste — we never scrape LinkedIn, which
# prohibits it in their Terms of Service)
# -----------------------------
with st.expander("🔗 LinkedIn Profile Analyzer (optional)"):
    st.caption(
        "Copy your Headline, About section, and a couple of Experience "
        "descriptions from your own LinkedIn profile page and paste them "
        "below. We don't fetch LinkedIn profiles automatically."
    )
    linkedin_text = st.text_area(
        "Paste your LinkedIn profile text here",
        height=200,
        placeholder="Headline: ...\n\nAbout: ...\n\nExperience: ...",
    )

# -----------------------------
# PROCESSING PIPELINE
# -----------------------------
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "version_history" not in st.session_state:
    st.session_state.version_history = []
if "job_recommendations" not in st.session_state:
    st.session_state.job_recommendations = None
if "linkedin_analysis" not in st.session_state:
    st.session_state.linkedin_analysis = None
if "last_analyzed_hash" not in st.session_state:
    st.session_state.last_analyzed_hash = None

auto_analyze = st.checkbox(
    "⚡ Auto-analyze as soon as both fields are filled",
    value=True,
    help=(
        "Runs automatically the moment your resume and primary job "
        "description both have content, and only re-runs if you actually "
        "change the text — not on unrelated clicks. Turn this off if you're "
        "close to today's Gemini API request limit (free tier: 20/day)."
    ),
)

col_analyze, col_recommend, col_linkedin = st.columns(3)

with col_analyze:
    run_analysis_clicked = st.button("Analyze Resume", type="primary")

with col_recommend:
    run_recommendations = st.button("🧭 Find Matching Job Roles")

with col_linkedin:
    run_linkedin = st.button("🔗 Analyze LinkedIn Profile")

# Auto-trigger only when the resume/job1 content has actually changed since
# the last successful run — prevents burning API quota on every unrelated
# rerun (switching tabs, opening the sidebar, etc.), since Streamlit reruns
# the whole script on any interaction.
current_input_hash = hashlib.sha256(f"{resume}||{job1}".encode()).hexdigest() if resume and job1 else None
auto_triggered = (
    auto_analyze
    and current_input_hash is not None
    and current_input_hash != st.session_state.last_analyzed_hash
)

run_analysis = run_analysis_clicked or auto_triggered

if run_recommendations:
    if not resume:
        st.warning("Please provide a resume first.")
    elif not gemini_enabled:
        st.error("Cannot generate recommendations. Gemini API is not configured.")
    else:
        with st.spinner("🧭 Matching your background against likely-fit roles..."):
            recommendation_prompt = f"""
            You are a career advisor. Based ONLY on the skills, experience, and
            background shown in this resume, recommend job roles this person is
            genuinely well-suited for — including roles they may not have
            considered.

            [RESUME]
            {resume}

            Return exactly 5 recommended job titles. For each one, use this
            exact format:

            ### [Job Title]
            **Why it fits:** 1-2 sentences tying it to specific evidence in the resume.
            **Search keywords:** 3 comma-separated terms to use on job boards for this role.
            """
            try:
                recommendation_text = generate_with_retry(recommendation_prompt)
                st.session_state.job_recommendations = recommendation_text
                st.success("Recommendations ready — see the '🧭 Job Recommendations' tab below.")
            except Exception as e:
                error_text = str(e).lower()
                if "429" in error_text:
                    st.error(
                        "You've hit today's Gemini API request limit (free tier allows 20/day). "
                        "It resets tomorrow, or you can enable billing on your Google AI Studio "
                        "project for higher limits."
                    )
                else:
                    st.error(f"Could not generate recommendations: {e}")

if run_linkedin:
    if not linkedin_text:
        st.warning("Please paste your LinkedIn profile text in the expander above first.")
    elif not gemini_enabled:
        st.error("Cannot analyze profile. Gemini API is not configured.")
    else:
        with st.spinner("🔗 Reviewing your LinkedIn profile..."):
            consistency_note = (
                f"\n\nAlso compare it against this resume for consistency "
                f"(flag any conflicting job titles, dates, or claims):\n[RESUME]\n{resume}"
                if resume else ""
            )
            linkedin_prompt = f"""
            You are a LinkedIn profile optimization expert. Review this
            profile content and provide feedback in exactly this format:

            ### Headline Assessment
            Is it keyword-rich and specific, or generic? Suggest a stronger version.

            ### About Section Assessment
            Does it read well and include searchable keywords? 2-3 concrete improvement suggestions.

            ### Experience Section Assessment
            Are the bullet points achievement-focused or just duty lists? Suggest 1-2 rewrites.

            ### Recruiter Searchability Score
            Score 1-10 with a one-sentence reason.

            ### Consistency Check
            Note any conflicts with the resume if one was provided, otherwise say "No resume provided for comparison."

            [LINKEDIN PROFILE TEXT]
            {linkedin_text}
            {consistency_note}
            """
            try:
                st.session_state.linkedin_analysis = generate_with_retry(linkedin_prompt)
                st.success("LinkedIn analysis ready — see the section below.")
            except Exception as e:
                error_text = str(e).lower()
                if "429" in error_text:
                    st.error(
                        "You've hit today's Gemini API request limit (free tier allows 20/day). "
                        "It resets tomorrow, or you can enable billing on your Google AI Studio "
                        "project for higher limits."
                    )
                else:
                    st.error(f"Could not analyze LinkedIn profile: {e}")

if run_analysis:
    if not resume or not job1:
        st.warning("Please provide at least a resume and the Primary Job Description.")
    elif not gemini_enabled:
        st.error("Cannot perform analysis. Gemini API is not configured.")
    else:
        with st.spinner("🤖 Remote Pilot AI is scanning your credentials and simulating ATS filtering..."):
            
            # Primary Keyword Calculations
            resume_words = set(resume.lower().split())
            job_words = set(job1.lower().split())
            matched_keywords = resume_words.intersection(job_words)
            missing_keywords = job_words - resume_words

            # Multi-Job Comparative Logic Calculations
            score1 = calculate_score(resume, job1)
            score2 = calculate_score(resume, job2) if job2 else 0
            score3 = calculate_score(resume, job3) if job3 else 0

            # Combined prompts for optimal single-token parsing
            master_prompt = f"""
            You are an expert corporate Recruiter and an advanced ATS parser.
            Analyze the following Resume against the Primary Job Description.

            [RESUME]
            {resume}

            [JOB DESCRIPTION]
            {job1}

            Provide a comprehensive evaluation divided explicitly into these sections using these exact headers:
            
            ### RESUME SUMMARY
            Provide a short, 3-sentence professional summary of the candidate's background relative to this job.

            ### CORE STRENGTHS
            List 3 major strengths or matching qualifications found in the resume.

            ### CRITICAL WEAKNESSES
            List 2-3 main gaps or formatting blocks keeping this resume from passing recruiters.

            ### INTERVIEW PREPARATION
            Provide 3 realistic interview questions tailored to this job role, along with high-scoring sample answers or talking points for this candidate.

            ### RESUME REWRITE SUGGESTIONS
            Provide a restructured, high-impact rewrite of the candidate's professional summary and their top experience bullet points, optimized with keywords to rank highly.

            ### CAREER COACH GUIDANCE
            Give 2-3 actionable career recommendations to permanently overcome the skill gaps discovered.

            ### TAILORED COVER LETTER
            Write a professional, compelling, 3-4 paragraph cover letter customized for this applicant applying to this specific role. Include placeholder tags like [Your Name] where appropriate.
            """

            scoring_prompt = f"""
            Score this resume from 1-10 on these parameters. Return your complete answer strictly formatted as markdown bullet points:
            - **Technical Skills**: [Score]/10
            - **Experience**: [Score]/10
            - **Leadership**: [Score]/10
            - **Communication**: [Score]/10
            - **ATS Compatibility**: [Score]/10

            Resume: {resume}
            Job Description: {job1}
            """

            try:
                # Each call retries automatically a couple of times on
                # transient failures before giving up.
                ai_text = generate_with_retry(master_prompt)
                score_text = generate_with_retry(scoring_prompt)

                def extract_section(text, header, next_header=None):
                    try:
                        part = text.split(header)[1]
                        if next_header:
                            part = part.split(next_header)[0]
                        return part.strip()
                    except IndexError:
                        # This means `header` literally wasn't found in the
                        # AI's response text. Printing to the terminal/logs
                        # lets YOU see it (users won't), so you can tell
                        # whether Gemini is drifting from the expected format.
                        print(f"[extract_section] Header not found: {header!r}")
                        return "Section layout mismatched. Please try analyzing again."

                # Commit metrics data mapping objects directly to permanent memory
                st.session_state.analysis_results = {
                    "score": calculate_score(resume, job1, boost=40),
                    "matched_count": len(matched_keywords),
                    "missing_skills": sorted(list(missing_keywords)),
                    "score1": score1,
                    "score2": score2,
                    "score3": score3,
                    "ai_score_breakdown": score_text,
                    "summary": extract_section(ai_text, "### RESUME SUMMARY", "### CORE STRENGTHS"),
                    "strengths": extract_section(ai_text, "### CORE STRENGTHS", "### CRITICAL WEAKNESSES"),
                    "weaknesses": extract_section(ai_text, "### CRITICAL WEAKNESSES", "### INTERVIEW PREPARATION"),
                    "interview": extract_section(ai_text, "### INTERVIEW PREPARATION", "### RESUME REWRITE SUGGESTIONS"),
                    "rewrite": extract_section(ai_text, "### RESUME REWRITE SUGGESTIONS", "### CAREER COACH GUIDANCE"),
                    "coach": extract_section(ai_text, "### CAREER COACH GUIDANCE", "### TAILORED COVER LETTER"),
                    "cover_letter": ai_text.split("### TAILORED COVER LETTER")[-1].strip()
                }
                st.session_state.last_analyzed_hash = current_input_hash
                if auto_triggered and not run_analysis_clicked:
                    st.success("⚡ Auto-analysis complete!")
                else:
                    st.success("Analysis Complete!")
            except Exception as e:
                # Mark this input as attempted even though it failed, so
                # auto-analyze doesn't keep retrying the same input on every
                # unrelated rerun. A manual button click can still retry it.
                st.session_state.last_analyzed_hash = current_input_hash
                error_text = str(e).lower()
                if "429" in error_text and "quota exceeded" in error_text:
                    st.error(
                        "You've hit today's Gemini API request limit (free tier allows 20/day). "
                        "It resets tomorrow, or you can enable billing on your Google AI Studio "
                        "project for higher limits."
                    )
                elif "429" in error_text or "rate" in error_text:
                    st.error("Gemini is rate-limiting requests right now. Please wait a minute and try again.")
                else:
                    st.error(f"An error occurred during AI processing: {str(e)}")

# -----------------------------
# JOB RECOMMENDATIONS (independent of full ATS analysis)
# -----------------------------
if st.session_state.job_recommendations:
    st.markdown("---")
    st.header("🧭 Recommended Job Roles")
    st.caption("Based on your resume alone — not tied to any specific job description above.")
    st.markdown(st.session_state.job_recommendations)

# -----------------------------
# LINKEDIN ANALYSIS (independent of full ATS analysis)
# -----------------------------
if st.session_state.linkedin_analysis:
    st.markdown("---")
    st.header("🔗 LinkedIn Profile Analysis")
    st.markdown(st.session_state.linkedin_analysis)

# -----------------------------
# RUNTIME UI DRAW RE-RENDER INTERFACE
# -----------------------------
if st.session_state.analysis_results:
    res = st.session_state.analysis_results

    # Top Metric Dashboard Cards Array
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("ATS Match Score", f"{res['score']}%")
    with m_col2:
        st.metric("Matched Keywords", res['matched_count'])
    with m_col3:
        st.metric("Missing Gaps", len(res['missing_skills']))
    with m_col4:
        word_count = len(resume.split()) if resume else 0
        st.metric("Resume Word Count", word_count if word_count > 0 else "—")
    
    st.progress(res['score'] / 100)

    # -----------------------------
    # SAVE THIS VERSION TO HISTORY
    # -----------------------------
    if st.button("💾 Save This Version to History"):
        st.session_state.version_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": res["score"],
            "matched_count": res["matched_count"],
            "missing_count": len(res["missing_skills"]),
            "resume_snapshot": resume,
            "job_snapshot": job1,
        })
        st.success(f"Saved! You now have {len(st.session_state.version_history)} version(s) in this session.")

    # -----------------------------
    # ON-DEMAND GENERATE PDF ENGINE
    # -----------------------------
    try:
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(pdf_file.name)
        c.drawString(100, 800, "ResumePilot AI Assessment Report")
        c.drawString(100, 770, f"Primary ATS Score: {res['score']}%")
        c.drawString(100, 740, f"Matched Keywords Found: {res['matched_count']}")
        c.drawString(100, 710, f"Missing Keywords Logged: {len(res['missing_skills'])}")
        c.save()
        
        with open(pdf_file.name, "rb") as f:
            st.download_button(
                label="📄 Download Executive Summary PDF Report",
                data=f,
                file_name="ResumePilot_Report.pdf",
                mime="application/pdf"
            )
    except Exception as pdf_err:
        st.info("PDF Summary compilation engine currently idling.")

    st.markdown("---")

    # Render Your Updated 10 Tabs System
    tabs = st.tabs([
        "📊 ATS Score", "🎯 Skill Gaps", "💡 Interview Tips", 
        "📝 Resume Summary", "🔍 Detailed Analysis", "✍️ Resume Rewrite", 
        "🧠 AI Coach", "✉️ Cover Letter", "📈 Job Comparison", "🕒 Version History"
    ])

    # Tab 1: ATS SCORE LAYOUT WITH PLOTLY PIE CHART
    with tabs[0]:
        st.header("ATS Match Optimization Breakdown")
        
        # Build Dataframe safely using dynamic variables mapped from session memory
        chart_data = pd.DataFrame({
            "Category": ["Matched Keywords", "Missing Deficiencies"],
            "Count": [res['matched_count'], max(len(res['missing_skills']), 1)]
        })
        fig = px.pie(chart_data, values="Count", names="Category", title="Core Keyword Metric Density Coverage")
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("Calculated Primary Matching Factor", f"{res['score']}%")
        if res['score'] >= 80:
            st.success("🏆 **Excellent Alignment:** Your profile shares close parity with the requirements of this role.")
        elif res['score'] >= 65:
            st.warning("⚡ **Moderate Alignment:** Good base, but missing target terms should be blended in.")
        else:
            st.error("❌ **Low Alignment:** Significant keyword gaps found. Automated parsers could reject this early.")

    # Tab 2: SKILL GAPS
    with tabs[1]:
        st.header("Target Keyword Deficiencies")
        st.write("These terms appear in your target specifications but were absent or phrased differently in your resume layout:")
        if res['missing_skills']:
            filtered_skills = [s for s in res['missing_skills'] if len(s) > 2 and s.isalpha()]
            st.write(", ".join([f"`{skill}`" for skill in filtered_skills[:30]]))
        else:
            st.success("Phenomenal keyword optimization! No major contextual metrics missing.")

    # Tab 3: INTERVIEW PREPARATION
    with tabs[2]:
        st.header("Tailored Interview Preparation Simulator")
        st.markdown(res['interview'])

    # Tab 4: RESUME SUMMARY
    with tabs[3]:
        st.header("Objective Profile Summary")
        st.write(res['summary'])

    # Tab 5: DETAILED ANALYSIS & RAW SCORES
    with tabs[4]:
        st.header("Comparative Structural Report")
        col_str, col_weak = st.columns(2)
        with col_str:
            st.subheader("✅ Structural Strengths")
            st.markdown(res['strengths'])
        with col_weak:
            st.subheader("⚠️ ATS Bottlenecks & Gaps")
            st.markdown(res['weaknesses'])
        
        st.markdown("---")
        st.subheader("AI Scoring Breakdown Matrix")
        st.markdown(res['ai_score_breakdown'])

    # Tab 6: REWRITE SUGGESTIONS
    with tabs[5]:
        st.header("ATS-Optimized Phrasing Suggestions")
        st.markdown(res['rewrite'])

    # Tab 7: CAREER COACHING
    with tabs[6]:
        st.header("Strategic Professional Development Plan")
        st.markdown(res['coach'])

    # Tab 8: TARGET COVER LETTER
    with tabs[7]:
        st.header("Custom Tailored Cover Letter Generator")
        st.text_area("Generated Output (Editable)", res['cover_letter'], height=450)

    # Tab 9: MULTI-JOB SCORING COMPARISON GRAPH
    with tabs[8]:
        st.header("Multi-Job Intent Target Comparison Chart")
        comparison_dict = {
            "Primary Job (Job 1)": res['score1'],
            "Comparison Job 2": res['score2'],
            "Comparison Job 3": res['score3']
        }
        st.bar_chart(comparison_dict)
        st.info("Use this visual data array to see which job profile variant matches best with your current resume version.")

    # Tab 10: VERSION HISTORY
    with tabs[9]:
        st.header("Resume Version History")
        st.caption(
            "Saved versions live only in this browser session. Use Export/Import "
            "below to keep your history across visits — no account needed."
        )

        history = st.session_state.version_history

        if not history:
            st.info("No versions saved yet. Click '💾 Save This Version to History' above after an analysis.")
        else:
            # Score trend over saved versions
            trend_df = pd.DataFrame({
                "Version": [f"v{i+1} ({h['timestamp']})" for i, h in enumerate(history)],
                "Score": [h["score"] for h in history],
            })
            fig_trend = px.line(trend_df, x="Version", y="Score", markers=True, title="ATS Score Across Saved Versions")
            st.plotly_chart(fig_trend, use_container_width=True)

            # Table of all saved versions
            table_df = pd.DataFrame([
                {
                    "Version": f"v{i+1}",
                    "Saved At": h["timestamp"],
                    "Score": f"{h['score']}%",
                    "Matched": h["matched_count"],
                    "Missing": h["missing_count"],
                }
                for i, h in enumerate(history)
            ])
            st.dataframe(table_df, use_container_width=True)

            # Reload an older version back into the working text areas
            reload_choice = st.selectbox(
                "Load an earlier version back into the editor above",
                options=list(range(len(history))),
                format_func=lambda i: f"v{i+1} — {history[i]['timestamp']} — {history[i]['score']}%",
            )
            if st.button("↩️ Load Selected Version"):
                st.session_state["_reload_resume"] = history[reload_choice]["resume_snapshot"]
                st.session_state["_reload_job1"] = history[reload_choice]["job_snapshot"]
                st.info("Loaded. Scroll up, the resume and job description fields are now populated — click Analyze Resume to re-run.")

            st.markdown("---")

            # Export / Import for cross-session persistence without accounts
            col_export, col_import = st.columns(2)
            with col_export:
                st.download_button(
                    "⬇️ Export History as JSON",
                    data=json.dumps(history, indent=2),
                    file_name="resumepilot_version_history.json",
                    mime="application/json",
                )
            with col_import:
                imported_file = st.file_uploader("⬆️ Import History JSON", type=["json"], key="history_import")
                if imported_file and st.button("Merge Imported History"):
                    try:
                        imported_data = json.loads(imported_file.read())
                        st.session_state.version_history.extend(imported_data)
                        st.success(f"Imported {len(imported_data)} version(s). Refresh the tab to see them.")
                    except Exception as e:
                        st.error(f"Could not read that file: {e}")

# -----------------------------
# SIDEBAR BACKEND TEST BUTTONS
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Infrastructure Connectivity Diagnostics")

if st.sidebar.button("Test Gemini Connection"):
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL, contents="Say hello"
        )
        st.sidebar.success(f"Gemini Active: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# NOTE: The old "Test AMD Llama Node" button hardcoded a raw server IP
# address directly in source code that was pushed to a PUBLIC GitHub repo.
# That let anyone reading your code hit your server directly, with no
# authentication. It has been removed entirely.
#
# If you need to test a second/local LLM endpoint later, put the URL in
# .streamlit/secrets.toml (which is .gitignored, so it never reaches GitHub)
# and read it with st.secrets["LLAMA_NODE_URL"] instead of typing it here.
