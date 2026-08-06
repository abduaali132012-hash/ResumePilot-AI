```python
# pages/6_🎤_AI_Interview_Coach.py
import json
import re

import streamlit as st
from google import genai

st.set_page_config(page_title="AI Interview Coach", page_icon="🎤", layout="wide")

MODEL = "gemini-2.0-flash"

ROLES = [
    "Software Engineer", "Frontend Engineer", "Backend Engineer", "Data Scientist",
    "Data Analyst", "ML Engineer", "DevOps Engineer", "Product Manager",
    "Project Manager", "UX Designer", "General",
]
LEVELS = ["Junior", "Mid-level", "Senior", "Lead/Principal"]


def get_client():
    key = st.secrets.get("GOOGLE_API_KEY")
    if not key:
        st.error("Missing `GOOGLE_API_KEY` in `.streamlit/secrets.toml`.")
        st.stop()
    return genai.Client(api_key=key)


def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
    return json.loads(text)


def generate_questions(client, role: str, level: str, count: int, language: str) -> list:
    prompt = (
        f"You are a hiring manager for a {level} {role} position. "
        f"Generate exactly {count} realistic interview questions mixing behavioral and technical questions. "
        f"Language: {language}. Return ONLY a JSON array of question strings."
    )
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    return parse_json(resp.text)


def evaluate_answer(client, role: str, level: str, question: str, answer: str, language: str) -> dict:
    prompt = (
        f"You are an interview coach preparing a candidate for a {level} {role} interview.\n\n"
        f"QUESTION:\n{question}\n\n"
        f"CANDIDATE ANSWER:\n{answer}\n\n"
        "Evaluate the answer and return ONLY JSON with keys: "
        '"score" (integer 0-10), "feedback" (2-3 encouraging sentences), '
        '"strengths" (array of 2-3 strings), "improvements" (array of 2-3 concrete suggestions), '
        f'"model_answer_pointer" (one sentence on what a strong answer covers). Language: {language}.'
    )
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    return parse_json(resp.text)


# ---------- Sidebar setup ----------
with st.sidebar:
    st.header("🎤 Interview Setup")
    role = st.selectbox("Target role", ROLES)
    level = st.selectbox("Experience level", LEVELS)
    language = st.selectbox("Language", ["English", "French", "Spanish", "German", "Arabic", "Amharic"])
    q_count = st.slider("Number of questions", 3, 10, 5)
    if st.button("🔄 Start new interview", use_container_width=True):
        for k in ["iq_questions", "iq_index", "iq_answers", "iq_feedback"]:
            st.session_state.pop(k, None)
        st.rerun()

st.title("🎤 AI Interview Coach")
st.caption("Practice with an AI interviewer that gives you instant, honest feedback.")

if "iq_questions" not in st.session_state:
    st.session_state["iq_questions"] = []
    st.session_state["iq_index"] = 0
    st.session_state["iq_answers"] = []
    st.session_state["iq_feedback"] = []

questions = st.session_state["iq_questions"]

if not questions:
    if st.button("🚀 Generate interview questions", type="primary"):
        client = get_client()
        with st.spinner("Preparing your interview…"):
            try:
                questions = generate_questions(client, role, level, q_count, language)
            except Exception as exc:
                st.error(f"We couldn't start the interview — try again. ({exc})")
                st.stop()
        st.session_state["iq_questions"] = questions
        st.session_state["iq_index"] = 0
        st.session_state["iq_answers"] = []
        st.session_state["iq_feedback"] = []
        st.rerun()
else:
    idx = st.session_state["iq_index"]
    done = len(st.session_state["iq_answers"])

    st.progress(min(done / len(questions), 1.0), text=f"Question {min(idx + 1, len(questions))} of {len(questions)}")

    if idx < len(questions):
        st.subheader(f"Question {idx + 1}")
        st.markdown(f"### {questions[idx]}")

        answer = st.text_area(
            "Your answer", height=180, key=f"answer_{idx}",
            placeholder="Type your answer as if speaking in the interview…",
        )
        col_a, col_b = st.columns([1, 3])
        with col_a:
            submit = st.button("📨 Submit answer", type="primary", use_container_width=True)
        with col_b:
            st.markdown("_Tip: use the STAR method — Situation, Task, Action, Result._")

        if submit and answer.strip():
            client = get_client()
            with st.spinner("Evaluating your answer…"):
                try:
                    feedback = evaluate_answer(client, role, level, questions[idx], answer, language)
                except Exception as exc:
                    st.error(f"We couldn't evaluate that answer — try again. ({exc})")
                    st.stop()
            st.session_state["iq_answers"].append(answer)
            st.session_state["iq_feedback"].append(feedback)
            st.session_state["iq_index"] += 1
            st.rerun()
        elif submit:
            st.warning("Please write an answer first.")
    else:
        st.success("🎉 Interview complete! Here is your summary.")
        scores = [f.get("score", 0) for f in st.session_state["iq_feedback"]]
        avg = sum(scores) / len(scores) if scores else 0
        c1, c2 = st.columns(2)
        c1.metric("Average score", f"{avg:.1f} / 10")
        c2.metric("Questions answered", len(scores))

        for i, (q, fb) in enumerate(zip(questions, st.session_state["iq_feedback"])):
            with st.expander(f"Q{i + 1} · {fb.get('score', 0)}/10 — {q[:70]}{'…' if len(q) > 70 else ''}"):
                st.markdown(f"**Your answer:**\n\n{st.session_state['iq_answers'][i]}")
                st.markdown(f"**Feedback:** {fb.get('feedback', '')}")
                st.markdown("**Strengths:** " + ", ".join(fb.get("strengths", [])))
                st.markdown("**Improvements:** " + ", ".join(fb.get("improvements", [])))
                st.markdown(f"**Model answer pointer:** {fb.get('model_answer_pointer', '')}")

        if st.button("🔁 Practice again", type="primary"):
            for k in ["iq_questions", "iq_index", "iq_answers", "iq_feedback"]:
                st.session_state.pop(k, None)
            st.rerun()
```
