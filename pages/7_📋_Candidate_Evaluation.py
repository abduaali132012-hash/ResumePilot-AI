# pages/7_📋_Candidate_Evaluation.py
"""
Evidence-Based Candidate Evaluation Agent
=========================================

Frontier Engineering Challenge 2026 (Micro1) work.

Turns ResumePilot from a single-pass "how good is this resume?" scorer into an
evidence-grounded candidate evaluation agent:

    Job Description → Requirement Extraction
    Candidate Resume → Evidence Extraction
    Matching → Evidence Verification → Human Review

Every requirement gets a verdict (SUPPORTED / PARTIALLY_SUPPORTED /
NOT_VERIFIED / NOT_FOUND) anchored to exact quotes from the resume, and a
human recruiter can then Confirm / Reject / flag for review each verdict.

The page degrades gracefully: if Gemini is unavailable or quota is exhausted,
it falls back to a deterministic keyword evaluator so the workflow never
hard-crashes.
"""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from ai.inference import GeminiClient
from ai.models import CandidateEvaluation, RequirementVerdict
from ai.pipeline import auto_evaluate, run_candidate_evaluation

st.set_page_config(
    page_title="Candidate Evidence Evaluation",
    page_icon="📋",
    layout="wide",
)

STATUS_EMOJI = {
    "SUPPORTED": "✅",
    "PARTIALLY_SUPPORTED": "⚠️",
    "NOT_VERIFIED": "❓",
    "NOT_FOUND": "❌",
}
STATUS_HELP = {
    "SUPPORTED": "Explicit, verifiable evidence found in the resume.",
    "PARTIALLY_SUPPORTED": "Indirect or weaker evidence only.",
    "NOT_VERIFIED": "Resume neither confirms nor clearly denies it.",
    "NOT_FOUND": "The requirement is clearly absent from the resume.",
}


def get_client() -> GeminiClient:
    client = GeminiClient()
    if not client.available:
        st.info(
            "⚠️ No Gemini key found — running in **deterministic fallback mode**. "
            "To use the full AI agents, add `GOOGLE_API_KEY` to "
            "`.streamlit/secrets.toml` (or Streamlit Cloud → Secrets)."
        )
    return client


def render_evaluation(ev: CandidateEvaluation) -> None:
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    counts = ev.status_counts()
    m1.metric("Evidence Coverage", f"{ev.overall_coverage:.0f}%")
    m2.metric("✅ Supported", counts["SUPPORTED"])
    m3.metric("⚠️ Partial", counts["PARTIALLY_SUPPORTED"])
    m4.metric("❌ Not verified/found", counts["NOT_VERIFIED"] + counts["NOT_FOUND"])

    st.progress(min(ev.overall_coverage / 100, 1.0))
    if ev.mode == "heuristic":
        st.caption("ℹ️ Results from the deterministic fallback (Gemini unavailable).")
    st.markdown(ev.summary)

    if not ev.verdicts:
        st.info("No requirements could be extracted — check that the job description is pasted.")
        return

    # ---------------- editable verdict table (human review) ----------------- #
    st.subheader("Requirement-by-Requirement Evidence Review")
    rows = []
    for i, v in enumerate(ev.verdicts):
        rows.append(
            {
                "id": i,
                "Requirement": v.requirement,
                "Category": v.category,
                "Status": v.status,
                "Evidence quote": v.evidence_quotes[0] if v.evidence_quotes else "—",
                "Confidence": v.confidence,
                "Review": v.review,
            }
        )
    df = pd.DataFrame(rows)

    edited = st.data_editor(
        df,
        column_config={
            "id": None,
            "Requirement": st.column_config.TextColumn("Requirement", width="medium"),
            "Status": st.column_config.TextColumn("Status", help="Verdict from the verifier agent."),
            "Evidence quote": st.column_config.TextColumn("Evidence quote", width="large"),
            "Review": st.column_config.SelectboxColumn(
                "Human review",
                options=["confirm", "reject", "needs_review"],
                help="Confirm, reject, or flag this verdict for review.",
                width="small",
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="verdict_editor",
    )

    # Persist human review decisions back into the evaluation.
    for i, row in edited.iterrows():
        verdict = ev.verdicts[int(row["id"])]
        verdict.review = row["Review"] if pd.notna(row["Review"]) else None

    # ---------------- per-requirement expanders ----------------------------- #
    st.subheader("Verdict Details & Evidence")
    for v in ev.verdicts:
        emoji = STATUS_EMOJI.get(v.status, "❓")
        reviewed = f" · 👤 {v.review}" if v.review else ""
        with st.expander(f"{emoji} {v.requirement} — {v.status}{reviewed}"):
            st.markdown(f"**Category:** {v.category}  ·  **Confidence:** {v.confidence}")
            st.markdown(f"**Notes:** {v.notes or '—'}")
            if v.evidence_quotes:
                st.markdown("**Supporting evidence (quotes):**")
                for q in v.evidence_quotes:
                    st.markdown(f"> {q}")
            else:
                st.caption("No supporting quote — the resume provides no verifiable evidence here.")

    # ---------------- export ------------------------------------------------- #
    col_exp, col_note = st.columns([1, 3])
    with col_exp:
        st.download_button(
            "⬇️ Export evaluation (JSON)",
            data=json.dumps(ev.to_dict(), ensure_ascii=False, indent=2),
            file_name="candidate_evaluation.json",
            mime="application/json",
        )
    with col_note:
        st.caption("Human review decisions (Confirm / Reject / Needs review) are included in the export.")


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
st.title("📋 Evidence-Based Candidate Evaluation Agent")
st.caption(
    "Frontier Engineering Challenge 2026 — evidence-grounded candidate evaluation. "
    "Requirements are matched to **quoted evidence** from the resume, verified by an "
    "AI agent, then reviewed by a human recruiter."
)

col_res, col_jd = st.columns(2)
with col_res:
    st.markdown("### Candidate Resume")
    uploaded = st.file_uploader(
        "Upload (PDF/DOCX/TXT)", type=["txt", "pdf", "docx"], key="ce_upload"
    )
    pasted_resume = st.text_area(
        "or paste resume text", height=320, key="ce_resume",
        placeholder="Paste the candidate's resume here…",
    )
    resume_text = pasted_resume
    if uploaded:
        try:
            raw = uploaded.getvalue()
            if uploaded.name.lower().endswith(".pdf"):
                import pdfplumber

                with pdfplumber.open(uploaded) as pdf:
                    resume_text = "\n".join((p.extract_text() or "") for p in pdf.pages)
            elif uploaded.name.lower().endswith(".docx"):
                from docx import Document

                resume_text = "\n".join(p.text for p in Document(uploaded).paragraphs)
            else:
                resume_text = raw.decode("utf-8", errors="ignore")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Couldn't read the uploaded file as text — use the paste box instead. ({exc})")

with col_jd:
    st.markdown("### Job Description")
    jd = st.text_area(
        "Paste the job description", height=360, key="ce_jd",
        placeholder="Paste the full job description here…",
    )

run_clicked = st.button("🚀 Run Candidate Evaluation", type="primary", use_container_width=True)

if run_clicked:
    if not resume_text or not resume_text.strip() or not jd or not jd.strip():
        st.warning("Please provide both a candidate resume and a job description.")
    else:
        with st.spinner("Extracting requirements, mining evidence, and verifying…"):
            try:
                client = get_client()
                if client.available:
                    ev = run_candidate_evaluation(resume_text, jd, client=client)
                else:
                    ev = auto_evaluate(resume_text, jd, client=client)
                st.session_state["ce_result"] = ev
                st.success("Evaluation complete.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"We couldn't run the evaluation — please try again. ({exc})")
                st.session_state.pop("ce_result", None)

if st.session_state.get("ce_result") is not None:
    render_evaluation(st.session_state["ce_result"])
elif not run_clicked:
    st.info(
        "Paste a **candidate resume** and a **job description**, then click "
        "**Run Candidate Evaluation**. The agent will extract the role's requirements, "
        "mine evidence from the resume, verify each requirement against that evidence, "
        "and let you review the verdicts."
    )
