uploaded_file = st.file_uploader(
"Upload Resume",
type=["txt", "pdf", "docx"]
)

resume = ""

if uploaded_file:

```
file_type = uploaded_file.name.split(".")[-1]

if file_type == "txt":
    resume = uploaded_file.read().decode("utf-8")

elif file_type == "pdf":

    with pdfplumber.open(uploaded_file) as pdf:

        for page in pdf.pages:
            resume += page.extract_text() or ""

elif file_type == "docx":

    doc = Document(uploaded_file)

    for para in doc.paragraphs:
        resume += para.text + "\n"

tab1, tab2, tab3 = st.tabs(...)
```
