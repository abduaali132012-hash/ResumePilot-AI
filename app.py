tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "ATS Score",
        "Skill Gaps",
        "Interview Tips",
        "Resume Summary",
        "Analysis"
    ]
)
with tab4:

    st.subheader("Resume Summary")

    word_count = len(resume.split())

    st.write(f"Resume Length: {word_count} words")

    if word_count < 150:
        st.warning(
            "Resume appears too short."
        )

    elif word_count > 800:
        st.warning(
            "Resume may be too long."
        )

    else:
        st.success(
            "Resume length looks good."
        )
        with tab5:

    st.subheader("Strength Analysis")

    strengths = []

    if score >= 70:
        strengths.append(
            "Strong keyword alignment"
        )

    if len(resume.split()) > 150:
        strengths.append(
            "Detailed resume content"
        )

    for item in strengths:
        st.success(item)
        st.subheader("Weakness Analysis")

if missing_skills:

    for skill in missing_skills[:5]:

        st.error(
            f"Missing keyword: {skill}"
        )

else:

    st.success(
        "No major weaknesses detected."
    )
    st.subheader("Recommendations")

st.info(
    "Add missing keywords from the job description."
)

st.info(
    "Quantify achievements using numbers."
)

st.info(
    "Customize resume for every application."
)

st.info(
    "Highlight relevant projects."
)
st.markdown("---")
if score >= 80:
    st.success("Excellent Match")

elif score >= 60:
    st.warning("Moderate Match")

else:
    st.error("Low Match")
