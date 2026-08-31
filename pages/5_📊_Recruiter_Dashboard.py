# pages/5_📊_Recruiter_Dashboard.py
import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai

st.set_page_config(page_title="Recruiter Dashboard", page_icon="📊", layout="wide")

MODEL = "gemini-2.5-flash"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "analyses.json"

SKILL_KEYWORDS = [
    "python", "react", "typescript", "javascript", "sql", "java", "go", "rust",
    "aws", "gcp", "azure", "docker", "kubernetes", "tensorflow", "pytorch",
    "machine learning", "data analysis", "excel", "tableau", "power bi",
    "project management", "agile", "scrum", "figma", "node.js", "django", "fastapi",
]


def get_client():
    key = st.secrets.get("GOOGLE_API_KEY")
    if not key:
        st.error("Missing `GOOGLE_API_KEY` in `.streamlit/secrets.toml`.")
        st.stop()
    return genai.Client(api_key=key)


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_analyses() -> list:
    ensure_data_dir()
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_analysis(entry: dict) -> None:
    records = [r for r in load_analyses() if r.get("file") != entry.get("file")]
    records.append(entry)
    ensure_data_dir()
    DATA_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
    return json.loads(text)


def rank_candidates(client, job_desc: str, resumes: list) -> list:
    payload = [{"file": name, "resume": text[:12000]} for name, text in resumes]
    prompt = (
        "You are an expert technical recruiter. Rank these candidates against the job description.\n\n"
        f"JOB DESCRIPTION:\n{job_desc}\n\n"
        f"CANDIDATES (JSON):\n{json.dumps(payload, ensure_ascii=False)}\n\n"
        'Return ONLY JSON: an array of objects with keys "file", "score" (0-100 integer), '
        '"match_summary" (one sentence), "key_strengths" (array of 3 strings), '
        '"red_flags" (array of strings, may be empty). Sort by score descending.'
    )
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    return parse_json(resp.text)


def extract_skills(text: str) -> list:
    lowered = text.lower()
    return [kw for kw in SKILL_KEYWORDS if kw in lowered]


tab_rank, tab_analytics = st.tabs(["📥 Rank Candidates", "📈 Analytics"])

with tab_rank:
    st.title("📥 Rank Candidates Against a Role")
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded = st.file_uploader(
            "Upload resumes (multiple)", type=["pdf", "txt", "md", "docx"], accept_multiple_files=True
        )
    with col2:
        job_title = st.text_input("Job title", placeholder="e.g. Senior Data Engineer")
        job_desc = st.text_area("Job description", height=220, placeholder="Paste the job description here…")

    if st.button("🚀 Rank candidates", type="primary", use_container_width=True):
        if not uploaded or not job_desc.strip():
            st.warning("Upload at least one resume and paste a job description.")
        else:
            client = get_client()
            resumes = []
            with st.spinner("Reading resumes…"):
                for f in uploaded:
                    try:
                        raw = f.getvalue().decode("utf-8", errors="ignore")
                    except Exception:
                        raw = ""
                    resumes.append((f.name, raw))
            with st.spinner("Scoring candidates with AI…"):
                try:
                    results = rank_candidates(client, job_desc, resumes)
                except Exception as exc:
                    st.error(f"We couldn't rank the candidates — please try again. ({exc})")
                    st.stop()

            results = sorted(results, key=lambda r: r.get("score", 0), reverse=True)
            df = pd.DataFrame(results)[["file", "score", "match_summary", "key_strengths", "red_flags"]]
            st.subheader("Ranked Candidates")
            st.dataframe(df, use_container_width=True, hide_index=True)

            chart_df = df[["file", "score"]].copy()
            chart_df["score"] = pd.to_numeric(chart_df["score"], errors="coerce")
            fig = px.bar(
                chart_df, x="file", y="score", color="score",
                color_continuous_scale="viridis", range_y=[0, 100],
                title="Candidate Match Scores",
            )
            st.plotly_chart(fig, use_container_width=True)

            for r in results:
                with st.expander(f"{r.get('score', 0)}/100 — {r.get('file')}"):
                    st.markdown(f"**Summary:** {r.get('match_summary', '')}")
                    st.markdown("**Key strengths:** " + ", ".join(r.get("key_strengths", [])))
                    flags = r.get("red_flags") or []
                    st.markdown("**Watch-outs:** " + (", ".join(flags) if flags else "None"))

            if st.button("💾 Save this ranking to analytics", use_container_width=True):
                for r in results:
                    save_analysis({
                        "file": r.get("file"),
                        "job_title": job_title or "Untitled role",
                        "score": r.get("score"),
                        "summary": r.get("match_summary", ""),
                        "strengths": r.get("key_strengths", []),
                        "flags": r.get("red_flags", []),
                    })
                st.success("Saved to analytics.")

with tab_analytics:
    st.title("📈 Candidate Analytics")
    records = load_analyses()
    if not records:
        st.info("No saved analyses yet. Rank candidates in the first tab and save the ranking to populate this dashboard.")
    else:
        df = pd.DataFrame(records)
        df["score"] = pd.to_numeric(df["score"], errors="coerce")

        m1, m2, m3 = st.columns(3)
        m1.metric("Candidates analyzed", len(df))
        m2.metric("Average score", f"{df['score'].mean():.1f}" if df["score"].notna().any() else "—")
        m3.metric("Top score", f"{df['score'].max():.0f}" if df["score"].notna().any() else "—")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(
                df, x="score", nbins=10, color_discrete_sequence=["#6366f1"],
                title="Score distribution",
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            by_role = df.groupby("job_title")["score"].mean().reset_index().sort_values("score", ascending=False)
            fig2 = px.bar(by_role, x="job_title", y="score", title="Average score by role")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Candidate pipeline")
        st.dataframe(df[["file", "job_title", "score", "summary"]], use_container_width=True, hide_index=True)