# ResumePilot AI — Evidence-Based Resume Evaluator

An agent skill for comparing a resume with a job description. It extracts
requirements, verifies them against resume quotes, explains evidence gaps,
suggests truthful improvements, and prepares interview questions.

## What it does

- Extracts required and preferred job qualifications.
- Maps qualifications to explicit evidence in a resume.
- Identifies supported, partially supported, unverified, and unfound evidence.
- Suggests truthful resume improvements and role-specific interview questions.
- Produces a structured, evidence-based evaluation report.

## Package contents

- `SKILL.md` — portable instructions for the AI agent.
- `README.md` — package overview and usage guide.

## How to use

Install or import the skill using the instructions for your AI agent. Provide
both a resume and the complete job description, then request an evidence-based
evaluation. For example:

> Compare my resume with this job description using the ResumePilot skill.
> Show each requirement, its priority, exact resume evidence, and whether it is
> supported, partially supported, not verified, or not found. Identify evidence
> gaps, suggest only truthful improvements, and prepare interview questions.
> Do not invent qualifications.

If either document is missing, the skill asks for it before comparing. Review
the report and verify every suggestion before using it.

## Example check

Give the agent a resume that says, “Built a Python inventory service backed by
SQL; used Git for version control,” and a posting requiring Python, SQL, Git,
FastAPI, and REST API development. The report should cite the supplied sentence
for Python and SQL, cite the Git statement for Git, and must not claim FastAPI
or REST API experience without resume evidence.

## Limitations

- This is decision-support guidance, not a hiring decision or a guarantee of
  ATS approval, an interview, or employment.
- Missing resume evidence does not prove that a candidate lacks a skill.
- AI output can be inaccurate; verify all claims, quotes, and recommendations.
- Avoid sharing personal candidate information unless you are comfortable
  sharing it with the AI service you use.
- Review the marketplace's current packaging, listing, compatibility, and payout
  requirements before publishing. No marketplace approval or earnings are
  guaranteed.

## Project

This package is a portable companion to the ResumePilot AI project; it is not
the full application or its API-backed evaluation pipeline.

- Repository: <https://github.com/abduaali132012-hash/ResumePilot-AI>
- Project evaluation pipeline: `ai/pipeline.py`
- Application: <https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk8.streamlit.app/>

## Creator

Abdu Ali Adem

## Marketplace listing draft

- **Title:** ResumePilot AI — Evidence-Based Resume Evaluator
- **Description:** Compare a resume with a job description using exact resume
  evidence. Identify supported and partially supported requirements, surface
  evidence gaps, improve resume wording honestly, and prepare for interviews.
- **Suggested tags:** Resume, CV, Job Search, Career, ATS, Interview Preparation
